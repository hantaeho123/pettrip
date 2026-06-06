import requests
import psycopg2
from dotenv import load_dotenv
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_KEY = os.getenv("KTO_API_KEY")
DB_URL  = os.getenv("DATABASE_URL")

def fetch_pet_places(page=1):
    # 매뉴얼 확인된 정확한 오퍼레이션: areaBasedList2
    full_url = (
        f"http://apis.data.go.kr/B551011/KorPetTourService2/areaBasedList2"
        f"?serviceKey={API_KEY}"
        f"&numOfRows=100"
        f"&pageNo={page}"
        f"&MobileOS=ETC"
        f"&MobileApp=PetTrip"
        f"&arrange=C"
        f"&_type=json"
    )

    print("요청 URL:", full_url[:80], "...")
    res = requests.get(full_url, verify=False, timeout=10)
    print("상태코드:", res.status_code)
    print("응답내용 앞부분:", res.text[:300])

    if res.status_code != 200 or "<html" in res.text.lower():
        print("❌ 실패")
        return []

    # XML로 오는 경우
    if res.text.strip().startswith("<"):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(res.text)
        # 에러 메시지 확인
        err = root.findtext(".//returnAuthMsg")
        if err:
            print(f"❌ API 에러: {err}")
            return []
        items = root.findall(".//item")
        result = []
        for item in items:
            result.append({
                "contentid":     item.findtext("contentid"),
                "title":         item.findtext("title"),
                "cat2":          item.findtext("cat2"),
                "mapy":          item.findtext("mapy"),
                "mapx":          item.findtext("mapx"),
                "acmpyPsblCpam": item.findtext("acmpyPsblCpam", "정보없음"),
            })
        return result

    # JSON으로 오는 경우
    data      = res.json()
    body      = data.get("response", {}).get("body", {})
    items_raw = body.get("items", {})
    if not items_raw:
        print("⚠️ 빈 응답")
        return []
    item_list = items_raw.get("item", [])
    if isinstance(item_list, dict):
        item_list = [item_list]
    return item_list


def save_to_db(items):
    if not items:
        print("저장할 데이터 없음")
        return

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()
    saved = 0
    for item in items:
        try:
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
                item.get("acmpyPsblCpam", "정보없음"),
            ))
            saved += 1
        except Exception as e:
            print(f"저장 실패: {e}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {saved}개 저장 완료!")


if __name__ == "__main__":
    print("📡 관광공사 전국 데이터 수집 시작!")
    total = 0
    page  = 1

    while True:
        print(f"\n--- {page}페이지 요청 중 ---")
        items = fetch_pet_places(page=page)

        if not items:
            print("✅ 더 이상 데이터 없음. 완료!")
            break

        save_to_db(items)
        total += len(items)
        print(f"누적 저장: {total}개")

        if len(items) < 100:   # 100개 미만이면 마지막 페이지
            print("✅ 마지막 페이지 완료!")
            break

        page += 1

    print(f"\n🎉 전체 완료! 총 {total}개 저장됨")