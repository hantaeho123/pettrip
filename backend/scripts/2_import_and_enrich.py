"""
scripts/2_import_and_enrich.py
이미 확보한 CSV(data.txt)를 kto_pet_places에 적재하고,
비어 있는 메타데이터(카테고리/동반정책/실내외 등)를 가공/추론으로 채운다.

실제 API의 areaBasedList는 카테고리/정책이 비어있는 경우가 많아서,
장소명 키워드 기반으로 카테고리를 추론하고 동반 정책을 합성한다.
이렇게 하면 필터링·랭킹 기능이 의미 있게 동작한다.

실행: python scripts/2_import_and_enrich.py data.txt
"""

import csv
import sys
import random
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# ── 장소명 키워드 → 카테고리 추론 규칙 ─────────────────────────────
CATEGORY_RULES = [
    (["카페", "커피", "coffee", "cafe", "베이커리", "디저트"], "카페"),
    (["식당", "맛집", "레스토랑", "식육", "고기", "한식", "분식", "국밥",
      "치킨", "피자", "버거", "파스타", "횟집", "막국수", "칼국수", "식탁",
      "주방", "키친", "그릴", "다이닝", "포차", "술집", "비스트로"], "식당"),
    (["호텔", "펜션", "리조트", "스테이", "민박", "게스트", "글램핑",
      "캠핑", "모텔", "풀빌라", "한옥"], "숙소"),
    (["공원", "수목원", "정원", "산", "해수욕장", "호수", "계곡",
      "강", "둘레길", "출렁다리", "폭포", "park"], "공원"),
    (["박물관", "미술관", "전시", "기념관", "문화"], "문화시설"),
    (["올리브영", "마트", "쇼핑", "백화점", "아울렛", "시장"], "쇼핑"),
]

def infer_category(name):
    n = (name or "").lower()
    for keywords, cat in CATEGORY_RULES:
        if any(k.lower() in n for k in keywords):
            return cat
    return "관광지"   # 기본값

# ── 카테고리별 동반 정책 합성 재료 ─────────────────────────────────
SIZE_POLICIES = [
    ("전 견종 출입 가능", 50.0),
    ("대형견 동반 가능 (25kg 이하)", 25.0),
    ("중형견까지 가능 (20kg 미만)", 20.0),
    ("소형견만 가능 (10kg 미만)", 10.0),
    ("15kg 이하 동반 가능", 15.0),
]
NEED_MATTERS = [
    "리드줄(목줄) 필수 착용", "입마개 착용 권장", "배변봉투 지참 필수",
    "예방접종 증명 필요", "목줄 2m 이내 유지", "켄넬 이용 권장",
]
AMENITIES_POOL = [
    "배변패드, 식기 비치", "반려동물 전용 식기 제공", "물그릇 비치",
    "반려동물 방석 제공", "별도 비치품 없음",
]
PURCHASE_POOL = [
    "수제 간식 판매", "사료 판매", "반려동물 음료 판매", "구매 품목 없음",
]
RENTAL_POOL = [
    "개모차 대여", "켄넬 대여", "대여 품목 없음", "반려동물 구명조끼 대여",
]


def enrich_row(name, category):
    """카테고리에 맞는 동반 정책 메타데이터를 합성."""
    # 카페/식당은 소형~중형 위주, 공원/숙소는 대형견도 잘 받음
    if category in ("공원", "숙소"):
        size_txt, max_w = random.choice(SIZE_POLICIES[:3])  # 대형/중형/전견종 위주
    elif category in ("카페", "식당"):
        size_txt, max_w = random.choice(SIZE_POLICIES)
    else:
        size_txt, max_w = random.choice(SIZE_POLICIES)

    policy = random.choice(NEED_MATTERS)
    is_indoor = category in ("카페", "식당", "숙소", "문화시설", "쇼핑") and random.random() < 0.7
    has_yard  = category in ("공원", "숙소", "관광지") or random.random() < 0.3

    return {
        "category": category,
        "pet_size_limit": size_txt,
        "max_weight_limit": max_w,
        "pet_policy": policy,
        "amenities": random.choice(AMENITIES_POOL),
        "purchase_items": random.choice(PURCHASE_POOL),
        "rental_items": random.choice(RENTAL_POOL),
        "is_indoor_allowed": is_indoor,
        "has_outdoor_yard": has_yard,
        "operating_hours": random.choice(["09:00~18:00", "10:00~20:00", "11:00~22:00", "24시간", "10:00~19:00"]),
        "closed_days": random.choice(["연중무휴", "매주 월요일 휴무", "매주 화요일 휴무", "명절 당일 휴무"]),
        "parking_info": random.choice(["무료 주차 가능", "유료 주차", "인근 공영주차장 이용", "주차 불가"]),
    }


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data.txt"
    print(f"📂 CSV 파일 적재: {csv_path}")
    print("=" * 55)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    count = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            place_id  = row["place_id"].strip()
            name      = row["place_name"].strip()
            # 원본 카테고리가 비어있으면 추론
            raw_cat   = (row.get("category") or "").strip()
            category  = raw_cat if raw_cat else infer_category(name)

            meta = enrich_row(name, category)

            batch.append((
                place_id, name, meta["category"],
                row.get("latitude") or None, row.get("longitude") or None,
                meta["pet_size_limit"], meta["max_weight_limit"], meta["pet_policy"],
                meta["amenities"], meta["purchase_items"], meta["rental_items"],
                meta["is_indoor_allowed"], meta["has_outdoor_yard"],
                meta["operating_hours"], meta["closed_days"], meta["parking_info"],
            ))

            if len(batch) >= 500:
                cur.executemany("""
                    INSERT INTO kto_pet_places (
                        place_id, place_name, category, latitude, longitude,
                        pet_size_limit, max_weight_limit, pet_policy,
                        amenities, purchase_items, rental_items,
                        is_indoor_allowed, has_outdoor_yard,
                        operating_hours, closed_days, parking_info
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (place_id) DO UPDATE SET
                        place_name = EXCLUDED.place_name,
                        category   = EXCLUDED.category,
                        pet_size_limit = EXCLUDED.pet_size_limit,
                        max_weight_limit = EXCLUDED.max_weight_limit
                """, batch)
                conn.commit()
                count += len(batch)
                batch = []
                print(f"  ⏳ {count}개 적재...")

        if batch:
            cur.executemany("""
                INSERT INTO kto_pet_places (
                    place_id, place_name, category, latitude, longitude,
                    pet_size_limit, max_weight_limit, pet_policy,
                    amenities, purchase_items, rental_items,
                    is_indoor_allowed, has_outdoor_yard,
                    operating_hours, closed_days, parking_info
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (place_id) DO UPDATE SET
                    place_name = EXCLUDED.place_name,
                    category   = EXCLUDED.category
            """, batch)
            conn.commit()
            count += len(batch)

    # 카테고리 분포 출력
    cur.execute("SELECT category, COUNT(*) FROM kto_pet_places GROUP BY category ORDER BY COUNT(*) DESC")
    dist = cur.fetchall()

    cur.close()
    conn.close()

    print("=" * 55)
    print(f"🎉 완료! 총 {count}개 장소 적재")
    print("\n📊 카테고리 분포:")
    for cat, n in dist:
        print(f"   {cat}: {n}개")
