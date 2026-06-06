import requests
import psycopg2
from dotenv import load_dotenv
import os
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_KEY = os.getenv("KTO_API_KEY")
DB_URL  = os.getenv("DATABASE_URL")

def fetch_pet_places(page=1):
    # http로 시도 (공공데이터포털은 http도 지원)
    url = "https://www.data.go.kr/data/15135102/openapi.do#/API%20%EB%AA%A9%EB%A1%9D/detailPetTour2"
    params = {
        "serviceKey": API_KEY,
        "numOfRows":  100,
        "pageNo":     page,
        "MobileOS":   "ETC",
        "MobileApp":  "PetTrip",
        "_type":      "json",
    }

    # SSL 검증 끄고 시도
    res = requests.get(url, params=params, verify=False, timeout=10)

    print("상태코드:", res.status_code)
    print("응답내용:", res.text[:300])

    if res.status_code != 200:
        print("❌ 실패. URL이 틀렸을 수 있어요.")
        return []

    data = res.json()

    # 응답 구조 확인
    body = data.get("response", {}).get("body", {})
    items_raw = body.get("items", {})

    if not items_raw or items_raw == "":
        print("⚠️ 데이터 없음 (빈 응답)")
        return []

    items = items_raw.get("item", [])
    if isinstance(items, dict):  # 1개일 때 리스트 아닌 dict로 올 수 있음
        items = [items]

    return items


def save_to_db(items):
    if not items:
        print("저장할 데이터가 없습니다.")
        return

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    for item in items:
        cur.execute("""
            INSERT INTO kto_pet_places
                (place_id, place_name, category, latitude, longitude, pet_policy)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (place_id) DO UPDATE SET
                place_name = EXCLUDED.place_name,
                category   = EXCLUDED.category,
                latitude   = EXCLUDED.latitude,
                longitude  = EXCLUDED.longitude,
                pet_policy = EXCLUDED.pet_policy;
        """, (
            str(item.get("contentid")),
            item.get("title"),
            item.get("cat2"),
            item.get("mapy"),
            item.get("mapx"),
            item.get("acmpyPsblCpam", "정보 없음"),
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {len(items)}개 저장 완료!")


if __name__ == "__main__":
    print("📡 관광공사 API 호출 중...")
    items = fetch_pet_places(page=1)
    if items:
        print(f"📦 {len(items)}개 데이터 받아옴")
        save_to_db(items)