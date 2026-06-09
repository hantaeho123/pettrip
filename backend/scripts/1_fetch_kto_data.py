"""
scripts/1_fetch_kto_data.py
한국관광공사 반려동물 동반여행 API에서 '실제' 장소 데이터를 수집하여
kto_pet_places 테이블에 저장한다.

⚠️ 이 스크립트가 kto_pet_places의 정식 데이터 소스다.
   (모든 API 컬럼은 반드시 API 응답에서만 채워진다. 임의 합성 금지)

사용하는 오퍼레이션 (모두 KorPetTourService2):
  ① petTourSyncList2 : 반려동물 동반 장소 '목록' (콘텐츠ID, 카테고리, 좌표, 주소, 대표이미지, 전화)
  ② detailPetTour2   : 장소별 '반려동물 상세' (동반가능동물/필요사항/비치·구매·렌탈품목/사고대비/기타)
  ③ detailIntro2     : 장소별 '운영 정보' (영업시간/휴무일/주차) — 카테고리별 필드명 다름
  ④ detailCommon2    : 장소별 '공통 정보' (홈페이지 URL)

매뉴얼 기준 호출 규칙:
  - http (https 아님), verify=False
  - serviceKey는 '디코딩 키'를 URL에 직접 붙임
  - _type=json

실행:
  python scripts/1_fetch_kto_data.py            # 전체 수집
  python scripts/1_fetch_kto_data.py 50         # 테스트로 50개만 수집
"""

import sys
import os
import re
import time
import requests
import psycopg2
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
API_KEY = os.getenv("KTO_API_KEY")
DB_URL  = os.getenv("DATABASE_URL")

BASE = "http://apis.data.go.kr/B551011/KorPetTourService2"
COMMON = "MobileOS=ETC&MobileApp=PetTrip&_type=json"

# contenttypeid → 사람이 읽는 카테고리
CONTENT_TYPE_MAP = {
    "12": "관광지", "14": "문화시설", "15": "행사공연축제",
    "28": "레포츠", "32": "숙소", "38": "쇼핑", "39": "식당",
}

# detailIntro2의 운영정보 필드명은 카테고리(contenttypeid)마다 다르다.
# (영업시간 필드, 휴무일 필드, 주차 필드) 순서
INTRO_FIELDS = {
    "12": ("usetime",        "restdate",         "parking"),          # 관광지
    "14": ("usetimeculture", "restdateculture",  "parkingculture"),   # 문화시설
    "15": ("playtime",       "",                 "parking"),          # 행사
    "28": ("usetimeleports", "restdateleports",  "parkingleports"),   # 레포츠
    "32": ("checkintime",    "",                 "parkinglodging"),   # 숙박 (휴무 없음)
    "38": ("opentime",       "restdateshopping", "parkingshopping"),  # 쇼핑
    "39": ("opentimefood",   "restdatefood",     "parkingfood"),      # 음식점
}


# ──────────────────────────────────────────────────────────────────
#  가공 컬럼 derive 함수 (보고서에 '가공 데이터'로 명시된 컬럼만)
# ──────────────────────────────────────────────────────────────────
def parse_max_weight(acmpy_psbl_cpam):
    """
    동반가능동물(acmpyPsblCpam) 텍스트에서 '수치 비교용 최대 몸무게'를 추출.
    예) "10kg 미만 소형견" → 10.0 / "전 견종 출입 가능" → 50.0
    (보고서: max_weight_limit = "[필터링 고도화] 수치 비교용 최대 몸무게")
    """
    if not acmpy_psbl_cpam:
        return None
    t = acmpy_psbl_cpam
    m = re.search(r'(\d+(?:\.\d+)?)\s*kg', t)
    if m:
        return float(m.group(1))
    if "전" in t and "견종" in t:   # 전 견종 출입 가능
        return 50.0
    if "대형" in t:
        return 40.0
    if "중형" in t:
        return 20.0
    if "소형" in t:
        return 10.0
    return None


def derive_indoor_outdoor(detail):
    """
    is_indoor_allowed / has_outdoor_yard 추정 (보고서: '가공 데이터').
    반려동물 상세의 여러 텍스트를 합쳐 키워드로 판단.
    """
    blob = " ".join(str(detail.get(k, "")) for k in [
        "acmpyPsblCpam", "acmpyNeedMtr", "etcAcmpyInfo",
        "relaPosesFclty", "acmpyTypeCd",
    ])
    is_indoor = ("실내" in blob) or ("내부" in blob)
    has_yard  = any(k in blob for k in ["야외", "마당", "테라스", "정원", "운동장"])
    return is_indoor, has_yard


# ──────────────────────────────────────────────────────────────────
#  API 호출 함수
# ──────────────────────────────────────────────────────────────────
def _get_json(url):
    """공통 GET → JSON items 리스트 반환 (실패 시 빈 값)."""
    try:
        res = requests.get(url, verify=False, timeout=(5, 15))  # (연결 5초, 읽기 15초)
        if res.status_code != 200:
            return None
        body = res.json().get("response", {}).get("body", {})
        items = (body.get("items") or {})
        if items == "" or items is None:
            return []
        item = items.get("item", [])
        return item if isinstance(item, list) else [item]
    except Exception:
        return None


def fetch_sync_list(page, rows=100):
    """① 반려동물 동반 장소 목록 (페이지 단위)."""
    url = f"{BASE}/petTourSyncList2?serviceKey={API_KEY}&numOfRows={rows}&pageNo={page}&{COMMON}&showflag=1"
    return _get_json(url)


def fetch_pet_detail(content_id):
    """② 반려동물 동반 상세 (장소별)."""
    url = f"{BASE}/detailPetTour2?serviceKey={API_KEY}&numOfRows=10&pageNo=1&{COMMON}&contentId={content_id}"
    items = _get_json(url)
    return items[0] if items else {}


def fetch_intro(content_id, content_type_id):
    """③ 소개정보(운영시간/휴무/주차) — 장소별."""
    url = f"{BASE}/detailIntro2?serviceKey={API_KEY}&numOfRows=10&pageNo=1&{COMMON}&contentId={content_id}&contentTypeId={content_type_id}"
    items = _get_json(url)
    return items[0] if items else {}


def fetch_common(content_id):
    """④ 공통정보(홈페이지) — 장소별."""
    url = f"{BASE}/detailCommon2?serviceKey={API_KEY}&numOfRows=10&pageNo=1&{COMMON}&contentId={content_id}"
    items = _get_json(url)
    return items[0] if items else {}


def clean_homepage(raw):
    """homepage 필드는 <a href="..."> HTML로 오는 경우가 많아 URL만 추출."""
    if not raw:
        return None
    m = re.search(r'href=["\']?(https?://[^"\'>\s]+)', raw)
    return m.group(1) if m else (raw if raw.startswith("http") else None)


# ──────────────────────────────────────────────────────────────────
#  저장
# ──────────────────────────────────────────────────────────────────
def save_place(cur, item, pet, intro, common, fetch_operating):
    cid  = str(item.get("contentid"))
    ctid = str(item.get("contenttypeid"))

    # ── 목록(petTourSyncList2)에서 오는 기본 정보 ──
    place_name = item.get("title")
    category   = CONTENT_TYPE_MAP.get(ctid, "기타")
    address    = f"{item.get('addr1','')} {item.get('addr2','')}".strip()
    mapx       = item.get("mapx") or None   # 경도
    mapy       = item.get("mapy") or None   # 위도
    main_image = item.get("firstimage") or None
    tel        = item.get("tel") or None

    # ── 반려동물 상세(detailPetTour2)에서 오는 API 컬럼 (직접 매핑) ──
    pet_size  = pet.get("acmpyPsblCpam") or None     # 동반 가능 동물
    policy    = pet.get("acmpyNeedMtr") or None       # 동반 시 필요사항
    type_cd   = pet.get("acmpyTypeCd") or None        # 동반 유형
    amenities = pet.get("relaFrnshPrdlst") or None    # 비치 품목
    purchase  = pet.get("relaPurcPrdlst") or None     # 구매 품목
    rental    = pet.get("relaRntlPrdlst") or None     # 대여 품목
    hazards   = pet.get("relaAcdntRiskMtr") or None   # 사고 대비사항
    extra     = pet.get("etcAcmpyInfo") or None        # 기타 동반 정보

    # ── 가공 컬럼 (보고서 '가공 데이터' 명시 컬럼만) ──
    max_w = parse_max_weight(pet_size)
    is_indoor, has_yard = derive_indoor_outdoor(pet)

    # ── 운영 정보(detailIntro2) / 홈페이지(detailCommon2) ──
    operating_hours = closed_days = parking_info = website = None
    if fetch_operating:
        f_use, f_rest, f_park = INTRO_FIELDS.get(ctid, ("usetime", "restdate", "parking"))
        operating_hours = (intro.get(f_use) or None) if f_use else None
        closed_days     = (intro.get(f_rest) or None) if f_rest else None
        parking_info    = (intro.get(f_park) or None) if f_park else None
        website         = clean_homepage(common.get("homepage"))

    cur.execute("""
        INSERT INTO kto_pet_places (
            place_id, place_name, category, address, latitude, longitude,
            pet_size_limit, max_weight_limit, pet_policy, pet_type_code,
            amenities, purchase_items, rental_items, safety_hazards, extra_info,
            main_image_url, operating_hours, closed_days, parking_info,
            contact_number, website_url, is_indoor_allowed, has_outdoor_yard
        ) VALUES (
            %s,%s,%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s,%s,
            %s,%s,%s,%s, %s,%s,%s,%s
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
            pet_type_code    = EXCLUDED.pet_type_code,
            amenities        = EXCLUDED.amenities,
            purchase_items   = EXCLUDED.purchase_items,
            rental_items     = EXCLUDED.rental_items,
            safety_hazards   = EXCLUDED.safety_hazards,
            extra_info       = EXCLUDED.extra_info,
            main_image_url   = EXCLUDED.main_image_url,
            operating_hours  = COALESCE(EXCLUDED.operating_hours, kto_pet_places.operating_hours),
            closed_days      = COALESCE(EXCLUDED.closed_days,     kto_pet_places.closed_days),
            parking_info     = COALESCE(EXCLUDED.parking_info,    kto_pet_places.parking_info),
            contact_number   = EXCLUDED.contact_number,
            website_url      = COALESCE(EXCLUDED.website_url, kto_pet_places.website_url),
            is_indoor_allowed= EXCLUDED.is_indoor_allowed,
            has_outdoor_yard = EXCLUDED.has_outdoor_yard
    """, (
        cid, place_name, category, address, mapy, mapx,
        pet_size, max_w, policy, type_cd,
        amenities, purchase, rental, hazards, extra,
        main_image, operating_hours, closed_days, parking_info,
        tel, website, is_indoor, has_yard,
    ))


# ──────────────────────────────────────────────────────────────────
#  메인
# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not API_KEY:
        print("❌ .env에 KTO_API_KEY가 없습니다. 공공데이터포털 디코딩 키를 넣어주세요.")
        sys.exit(1)

    # 인자로 테스트 개수 제한 (예: python 1_fetch_kto_data.py 50)
    test_limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    # 운영정보(intro/common)까지 가져올지: 장소당 호출이 2번 더 늘어 느려짐.
    # 기본 True (보고서의 운영정보 컬럼까지 실제 API로 채움)
    FETCH_OPERATING = True

    print("📡 한국관광공사 반려동물 동반여행 데이터 수집 (실제 API)")
    print(f"   - 반려동물 상세: detailPetTour2  (필수)")
    print(f"   - 운영 정보   : detailIntro2 + detailCommon2  ({'ON' if FETCH_OPERATING else 'OFF'})")
    if test_limit:
        print(f"   - ⚠️ 테스트 모드: 최대 {test_limit}개만 수집")
    print("=" * 60)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    total = 0
    page  = 1
    stop  = False

    while not stop:
        items = fetch_sync_list(page)
        if items is None:
            print(f"  ⚠️ {page}페이지 응답 오류 (키/네트워크 확인). 잠시 후 재시도...")
            time.sleep(2)
            items = fetch_sync_list(page)
            if items is None:
                break
        if not items:
            break

        for item in items:
            cid  = item.get("contentid")
            ctid = str(item.get("contenttypeid"))
            if not cid:
                continue

            try:
                # ② 반려동물 상세 (필수)
                pet = fetch_pet_detail(cid)

                # ③④ 운영정보·홈페이지 (선택, 실패해도 계속 진행)
                intro, common = {}, {}
                if FETCH_OPERATING:
                    try:
                        intro = fetch_intro(cid, ctid)
                    except Exception:
                        pass
                    try:
                        common = fetch_common(cid)
                    except Exception:
                        pass

                save_place(cur, item, pet, intro, common, FETCH_OPERATING)
                total += 1

                # 10개마다 진행률 표시
                if total % 10 == 0:
                    name = item.get("title", "")[:20]
                    print(f"    #{total} {name}... pet={'✓' if pet else '✗'} intro={'✓' if intro else '✗'}")

                time.sleep(0.04)   # API 부하 방지

            except Exception as e:
                print(f"    ⚠️ {cid} 처리 오류: {e}")
                continue

            if test_limit and total >= test_limit:
                stop = True
                break

        conn.commit()
        print(f"  ✅ {page}페이지 처리 | 누적 {total}개 저장")

        if len(items) < 100:
            break
        page += 1

    # 결과 요약
    cur.execute("SELECT category, COUNT(*) FROM kto_pet_places GROUP BY category ORDER BY COUNT(*) DESC")
    dist = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM kto_pet_places WHERE pet_size_limit IS NOT NULL")
    with_pet = cur.fetchone()[0]

    cur.close()
    conn.close()

    print("=" * 60)
    print(f"🎉 완료! 총 {total}개 장소 저장")
    print(f"   - 반려동물 동반정보가 있는 장소: {with_pet}개")
    print("\n📊 카테고리 분포:")
    for cat, n in dist:
        print(f"   {cat}: {n}개")