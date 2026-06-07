"""
scripts/1_fetch_kto_data.py
한국관광공사 반려동물 동반여행 API에서 실제 장소 데이터를 수집하여
kto_pet_places 테이블에 저장한다.

2단계로 동작:
  ① areaBasedList2  : 전국 장소 목록 (기본 정보 + 좌표)
  ② detailPetTour2  : 각 장소의 반려동물 상세 정보 (동반 정책 등)

contenttypeid → 카테고리 매핑, acmpyPsblCpam → max_weight_limit 추출 등
가공 로직 포함.

실행: python scripts/1_fetch_kto_data.py
"""

import requests
import psycopg2
from dotenv import load_dotenv
import os
import re
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
API_KEY = os.getenv("KTO_API_KEY")
DB_URL  = os.getenv("DATABASE_URL")

BASE = "http://apis.data.go.kr/B551011/KorPetTourService2"

# contenttypeid → 사람이 읽는 카테고리
CONTENT_TYPE_MAP = {
    "12": "관광지", "14": "문화시설", "15": "축제공연행사",
    "25": "여행코스", "28": "레포츠", "32": "숙소",
    "38": "쇼핑", "39": "식당",
}


def parse_max_weight(text):
    """
    동반 가능 동물 텍스트에서 최대 허용 몸무게를 추출.
    예: "10kg 미만 소형견" → 10.0 / "대형견 가능" → 40.0 / 없으면 None
    """
    if not text:
        return None
    # 'NNkg' 패턴 우선
    m = re.search(r'(\d+)\s*kg', text)
    if m:
        return float(m.group(1))
    # 견종 크기 키워드로 추정
    if "대형" in text:
        return 40.0
    if "중형" in text:
        return 20.0
    if "소형" in text:
        return 10.0
    if "전" in text and "견종" in text:   # 전 견종 가능
        return 50.0
    return None


def fetch_list(page, rows=100):
    """장소 목록 페이지 단위 조회."""
    url = (
        f"{BASE}/areaBasedList2"
        f"?serviceKey={API_KEY}"
        f"&numOfRows={rows}&pageNo={page}"
        f"&MobileOS=ETC&MobileApp=PetTrip&arrange=C&_type=json"
    )
    res = requests.get(url, verify=False, timeout=15)
    if res.status_code != 200:
        return []
    try:
        items = res.json()["response"]["body"]["items"].get("item", [])
        return items if isinstance(items, list) else [items]
    except Exception:
        return []


def fetch_detail(content_id):
    """특정 장소의 반려동물 상세 정보 조회."""
    url = (
        f"{BASE}/detailPetTour2"
        f"?serviceKey={API_KEY}"
        f"&numOfRows=10&pageNo=1"
        f"&MobileOS=ETC&MobileApp=PetTrip&_type=json"
        f"&contentId={content_id}"
    )
    try:
        res = requests.get(url, verify=False, timeout=15)
        items = res.json()["response"]["body"]["items"].get("item", [])
        items = items if isinstance(items, list) else [items]
        return items[0] if items else {}
    except Exception:
        return {}


def save_place(cur, item, detail):
    """목록 + 상세 정보를 합쳐 한 레코드로 저장."""
    pet_size = detail.get("acmpyPsblCpam", "")
    max_w    = parse_max_weight(pet_size)
    policy   = detail.get("acmpyNeedMtr", "")
    extra    = detail.get("etcAcmpyInfo", "")

    # 실내/야외 추정 (텍스트 기반 가공)
    full_text = f"{pet_size} {policy} {extra} {detail.get('relaPosesFclty','')}"
    is_indoor = "실내" in full_text
    has_yard  = ("야외" in full_text) or ("마당" in full_text) or ("테라스" in full_text)

    cur.execute("""
        INSERT INTO kto_pet_places (
            place_id, place_name, category, address, latitude, longitude,
            pet_size_limit, max_weight_limit, pet_policy, pet_type_code,
            amenities, purchase_items, rental_items, safety_hazards, extra_info,
            main_image_url, is_indoor_allowed, has_outdoor_yard
        ) VALUES (
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s
        )
        ON CONFLICT (place_id) DO UPDATE SET
            place_name       = EXCLUDED.place_name,
            category         = EXCLUDED.category,
            address          = EXCLUDED.address,
            latitude         = EXCLUDED.latitude,
            longitude        = EXCLUDED.longitude,
            pet_size_limit   = EXCLUDED.pet_size_limit,
            max_weight_limit = EXCLUDED.max_weight_limit,
            pet_policy       = EXCLUDED.pet_policy,
            is_indoor_allowed= EXCLUDED.is_indoor_allowed,
            has_outdoor_yard = EXCLUDED.has_outdoor_yard
    """, (
        str(item.get("contentid")),
        item.get("title"),
        CONTENT_TYPE_MAP.get(str(item.get("contenttypeid")), "기타"),
        f"{item.get('addr1','')} {item.get('addr2','')}".strip(),
        item.get("mapy") or None,
        item.get("mapx") or None,
        pet_size, max_w, policy, detail.get("acmpyTypeCd"),
        detail.get("relaFrnshPrdlst"), detail.get("relaPurcPrdlst"),
        detail.get("relaRntlPrdlst"), detail.get("relaAcdntRiskMtr"), extra,
        item.get("firstimage") or None,
        is_indoor, has_yard,
    ))


if __name__ == "__main__":
    print("📡 한국관광공사 반려동물 동반여행 데이터 수집 시작!")
    print("=" * 55)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    total = 0
    page  = 1
    FETCH_DETAIL = True   # 상세 정보까지 가져올지 (False면 목록만, 훨씬 빠름)

    while True:
        items = fetch_list(page)
        if not items:
            break

        for item in items:
            cid = item.get("contentid")
            detail = fetch_detail(cid) if FETCH_DETAIL else {}
            save_place(cur, item, detail)
            if FETCH_DETAIL:
                time.sleep(0.05)   # API 부하 방지

        conn.commit()
        total += len(items)
        print(f"  ✅ {page}페이지 완료 | 누적 {total}개")

        if len(items) < 100:
            break
        page += 1

    cur.close()
    conn.close()
    print("=" * 55)
    print(f"🎉 완료! 총 {total}개 장소 저장됨")
