"""
scripts/2_import_and_enrich.py
[보조 스크립트 / CSV 빠른 적재용]

⚠️ 중요: kto_pet_places의 'API 컬럼'(동반정책/시설/운영정보 등)은
   반드시 1_fetch_kto_data.py 로 실제 API에서 채워야 한다.
   이 스크립트는 그 API 컬럼을 임의로 만들어내지 않는다.

이 스크립트의 용도는 단 하나:
   네트워크 없이 빠르게 'place_id / place_name / category / 좌표'만 CSV에서 적재해
   지도가 일단 뜨도록 하는 용도. (반려동물 상세 컬럼은 NULL로 둔다)

CSV(data.txt) 컬럼: place_id, place_name, category, latitude, longitude, pet_policy
  - 실제 API 원본이라 category / pet_policy 대부분이 비어 있음
  - category가 비어 있으면 장소명 키워드로 '카테고리만' 추론 (이건 표시용 보조)
  - pet_policy 등 나머지 동반정보는 절대 합성하지 않고 NULL 유지

권장 사용 흐름:
   (A) 정식: python scripts/1_fetch_kto_data.py     ← API에서 전 컬럼 수집
   (B) 임시: python scripts/2_import_and_enrich.py data.txt  ← 좌표/이름만 빠르게

실행: python scripts/2_import_and_enrich.py data.txt
"""

import csv
import sys
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# 장소명 키워드 → 카테고리 추론 (표시용 보조. 동반정책과는 무관)
CATEGORY_RULES = [
    (["카페", "커피", "coffee", "cafe", "베이커리", "디저트", "로스터리"], "카페"),
    (["식당", "맛집", "레스토랑", "고기", "한식", "분식", "국밥", "치킨",
      "피자", "버거", "파스타", "횟집", "막국수", "칼국수", "식탁",
      "주방", "키친", "그릴", "다이닝", "포차", "비스트로"], "식당"),
    (["호텔", "펜션", "리조트", "스테이", "민박", "게스트", "글램핑",
      "캠핑", "모텔", "풀빌라", "한옥"], "숙소"),
    (["공원", "수목원", "정원", "산", "해수욕장", "호수", "계곡", "강",
      "둘레길", "출렁다리", "폭포", "park", "공원지"], "공원"),
    (["박물관", "미술관", "전시", "기념관", "문화"], "문화시설"),
    (["올리브영", "마트", "쇼핑", "백화점", "아울렛", "시장"], "쇼핑"),
]

def infer_category(name):
    n = (name or "").lower()
    for keywords, cat in CATEGORY_RULES:
        if any(k.lower() in n for k in keywords):
            return cat
    return "관광지"


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data.txt"
    print("📂 CSV 빠른 적재 (place_id / 이름 / 카테고리 / 좌표만)")
    print("   ⚠️ 반려동물 동반 상세 컬럼은 NULL로 둡니다.")
    print("      → 동반정보까지 채우려면 1_fetch_kto_data.py 를 실행하세요.")
    print("=" * 60)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    count = 0
    batch = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            place_id = row["place_id"].strip()
            name     = row["place_name"].strip()
            raw_cat  = (row.get("category") or "").strip()
            category = raw_cat if raw_cat else infer_category(name)
            lat      = row.get("latitude") or None
            lng      = row.get("longitude") or None
            # pet_policy는 CSV에 실제 값이 있을 때만 사용, '정보없음'/빈값은 NULL
            policy   = (row.get("pet_policy") or "").strip()
            if policy in ("", "정보없음", "정보 없음"):
                policy = None

            batch.append((place_id, name, category, lat, lng, policy))

            if len(batch) >= 500:
                cur.executemany("""
                    INSERT INTO kto_pet_places
                        (place_id, place_name, category, latitude, longitude, pet_policy)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (place_id) DO UPDATE SET
                        place_name = EXCLUDED.place_name,
                        category   = EXCLUDED.category,
                        latitude   = EXCLUDED.latitude,
                        longitude  = EXCLUDED.longitude
                """, batch)
                conn.commit()
                count += len(batch)
                batch = []
                print(f"  ⏳ {count}개 적재...")

        if batch:
            cur.executemany("""
                INSERT INTO kto_pet_places
                    (place_id, place_name, category, latitude, longitude, pet_policy)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (place_id) DO UPDATE SET
                    place_name = EXCLUDED.place_name,
                    category   = EXCLUDED.category
            """, batch)
            conn.commit()
            count += len(batch)

    cur.execute("SELECT category, COUNT(*) FROM kto_pet_places GROUP BY category ORDER BY COUNT(*) DESC")
    dist = cur.fetchall()
    cur.close()
    conn.close()

    print("=" * 60)
    print(f"🎉 완료! 총 {count}개 장소 적재 (좌표/이름/카테고리)")
    print("\n📊 카테고리 분포:")
    for cat, n in dist:
        print(f"   {cat}: {n}개")
    print("\n💡 반려동물 동반 상세(동반가능견종/필요사항/시설/운영시간 등)는")
    print("   아직 비어 있습니다. 'python scripts/1_fetch_kto_data.py'로 채우세요.")
