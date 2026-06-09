"""
scripts/3_generate_dummy_data.py
가상 데이터(app_users, pets, user_pet_map, place_reviews) 대량 생성기

장소 약 1만 개 규모에 걸맞게:
  - 유저      5,000명
  - 반려동물  6,000마리
  - 매핑      유저당 1마리 + 공동소유 일부
  - 리뷰      장소당 1~39개 (조합형으로 수십만 가지 문장 다양성)

리뷰 문장은 [계절·날씨·시간·동행·이동수단·장소묘사·반려동물반응·시설·마무리]를
조합해 만들기 때문에 사실상 거의 모든 리뷰가 다르게 보인다.

일부 리뷰에는 photo_url을 부여해 자랑게시판 피드가 채워지도록 한다.

실행: python scripts/3_generate_dummy_data.py
"""

import random
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

USER_COUNT = 5000
PET_COUNT  = 6000
PHOTO_RATIO = 0.12   # 리뷰 중 사진 첨부 비율

# ══════════════════════════════════════════════════════════════════
#  닉네임/펫이름/견종 풀
# ══════════════════════════════════════════════════════════════════
FIRST = ["초코","벨라","콩이","두부","루이","해피","뭉치","나비","보리","코코","몽이","땅콩",
         "솜이","구름","달이","별이","하루","봄이","여름","가을","겨울","복이","방울","노을",
         "새벽","햇살","바람","이슬","무지개","은하","별빛","새싹","꽃잎","단풍","눈꽃","서리",
         "안개","파도","모래","하늘","소나기","천둥","번개","이랑","물결","연두","보라","노랑",
         "분홍","아롱","다롱","뽀미","꼬미","토리","몰리","맥스","찰리","버디","럭키","쿠키",
         "도넛","마카롱","크림","푸딩","젤리","바닐라","민트","레몬","망고","딸기","복숭아",
         "사과","포도","감귤","키위","달콩","말랑","보들","따뜻","포근","사랑","행복","설레",
         "빛나","반짝","통통","동글","방긋","생긋","동동","살랑","포슬","폭신","말캉","보송",
         "탱글","몽글","까망","하양","점박","얼룩","폼폼","뭉게"]
SECOND = ["아빠","맘","네","댁","엄마","집사","주인","보호자","친구","가족","파파","마마",
          "오빠","언니","누나","형","삼촌","이모","할머니","할아버지"]
SUFFIX = ["","","","1","2","3","7","99","_kr","_pet","love","happy","99","00","07","24"]

BREEDS = ["골든리트리버","말티즈","포메라니안","시바이누","웰시코기","비숑프리제","토이푸들",
          "치와와","닥스훈트","보더콜리","래브라도리트리버","허스키","진돗개","불독","비글",
          "슈나우저","요크셔테리어","사모예드","아키타","셰퍼드","코커스패니얼","달마시안",
          "그레이하운드","바셋하운드","퍼그","샤페이","차우차우","말라뮤트","도베르만","삽살개",
          "스피츠","파피용","시츄","페키니즈","라사압소","뉴펀들랜드","세인트버나드","폭스테리어",
          "그레이트데인","아이리시세터","와이마라너","비즐라","이탈리안그레이하운드","믹스견"]

PET_NAMES = FIRST[:75]

# ══════════════════════════════════════════════════════════════════
#  리뷰 조합 재료
# ══════════════════════════════════════════════════════════════════
SEASONS    = ["봄","여름","가을","겨울"]
WEATHERS   = ["맑은 날","흐린 날","비 온 뒤","선선한 날","더운 날","쌀쌀한 날","눈 오는 날"]
TIMES      = ["오전에","점심때","오후에","저녁 무렵","주말에","평일 아침에","연휴에","황금연휴에"]
COMPANIONS = ["강아지랑 둘이서","가족이랑 함께","친구랑 같이","커플로","혼자 강아지 데리고","반려인 모임으로"]
TRANSPORT  = ["차 타고","대중교통으로","자전거 타고","걸어서","킥보드 타고"]

PLACE_DESC = {
    "카페": ["아늑한","탁 트인 테라스가 있는","아기자기한","빈티지 감성의","모던한","숲속 느낌의",
              "한옥 스타일의","루프탑이 멋진","뷰가 끝내주는","조용하고 한적한","인스타 감성 넘치는",
              "원목 인테리어의","따뜻한 조명의","세련된","감성적인"],
    "식당": ["현지인 맛집으로 소문난","양이 푸짐한","깔끔하고 정갈한","가성비 최고인","분위기 있는",
              "전통 느낌의","캐주얼한","고급스러운","아늑한","활기찬","정성이 느껴지는",
              "사장님이 친절한","오래된 단골 느낌의","신선한 재료를 쓰는"],
    "숙소": ["아늑하고 깨끗한","넓은 마당이 있는","자연 속에 있는","리조트 같은","감성 넘치는",
              "조용하고 프라이빗한","바다가 보이는","산 속의","도심 속 오아시스 같은",
              "반려견 전용 시설이 완비된","풀빌라 같은","캠핑 느낌의","한옥 느낌의"],
    "공원": ["넓고 쾌적한","잔디가 잘 깔린","나무 그늘이 많은","산책로가 잘 정비된","탁 트인",
              "호수가 있는","꽃이 만발한","단풍이 드는","눈 덮인","시원한 바람이 부는",
              "반려동물 전용 구역이 있는","잘 관리된","자연 그대로의"],
    "관광지": ["역사 깊은","경치가 아름다운","포토스팟이 많은","숨겨진 명소인","접근성이 좋은",
                "현지 감성 넘치는","자연친화적인","웅장한","아기자기한","계절마다 다른 매력의",
                "야경이 멋진","일출/일몰 명소인"],
}
DEFAULT_DESC = ["분위기 있는","깔끔한","넓은","아늑한","쾌적한","매력적인","독특한"]

PET_REACT = [
    "{n}이(가) 꼬리를 쉴 새 없이 흔들었어요","{n}이(가) 냄새 맡느라 여념이 없었어요 ㅋㅋ",
    "{n}이(가) 다른 강아지들이랑 금방 친해졌어요","{n}이(가) 엄청 신나서 뛰어다녔어요",
    "{n}이(가) 낯선 환경인데도 금방 적응했어요","{n}이(가) 처음엔 긴장했는데 곧 편안해했어요",
    "{n}이(가) 간식 냄새 맡고 눈을 반짝반짝했어요","{n}이(가) 산책하면서 완전 행복해 보였어요",
    "{n}이(가) 돌아가기 싫었는지 한참 버텼어요 ㅎㅎ","{n}이(가) 지쳐서 차에서 바로 잠들었어요",
    "{n}이(가) 풀밭에서 데굴데굴 구르며 놀았어요","{n}이(가) 직원분께 애교 부리며 간식 받아먹었어요",
    "{n}이(가) 사진 찍을 때마다 포즈 취해줬어요 ㅋㅋ","{n}이(가) 다른 손님들한테 인기 폭발이었어요",
    "{n}이(가) 강아지 친구 사귀고 놀더니 지쳐버렸어요","{n}이(가) 탐정처럼 바닥 냄새를 맡고 다녔어요",
    "{n}이(가) 밥도 잘 먹고 산책도 실컷 했어요","{n}이(가) 낯선 사람한테도 꼬리 흔들며 인사했어요",
]

FACILITY = [
    "물그릇을 따로 갖다주셔서 감동이었어요","강아지 전용 간식도 팔아서 너무 좋았어요",
    "펫 전용 입구가 따로 있어서 편했어요","야외 테라스가 넓어서 여유로웠어요",
    "강아지 목줄 걸이가 곳곳에 있어서 편리했어요","화장실이 깔끔하게 관리되고 있었어요",
    "주차 공간이 넉넉해서 편하게 왔어요","대형견도 편하게 이동할 수 있어서 좋았어요",
    "반려동물 입장 안내가 잘 되어 있었어요","배변봉투가 비치되어 있어서 편리했어요",
    "포토존이 있어서 예쁜 사진 많이 찍었어요","실내도 동반 가능해서 날씨 걱정 없었어요",
    "직원분들이 강아지를 무서워하지 않아서 좋았어요","산책로가 잘 정비되어 발바닥 걱정 없었어요",
    "반려견 전용 놀이 공간이 따로 있었어요","그늘이 충분해서 더운 날에도 괜찮았어요",
    "입장료가 없어서 부담 없이 다녀왔어요","매장이 넓어서 강아지가 부딪힐 걱정 없었어요",
    "강아지용 메뉴가 따로 있어서 놀랐어요","반려동물 방석까지 챙겨주셔서 세심했어요",
]

POS_END = ["다음에 꼭 또 올게요! 🐾","강아지 키우는 분들께 강력 추천드려요!","반려견 여행지로 최고예요 ✨",
           "단골이 될 것 같아요 ㅎㅎ","주변 반려인들한테도 다 알렸어요!","사진도 잘 나오고 강아지도 행복해했어요 📸",
           "멀리서 왔는데 올 가치 충분했어요!","이런 곳이 더 많아지면 좋겠어요","반려동물 친화적인 곳 찾으면 여기예요!",
           "오래오래 운영해주세요 🙏","재방문 100% 예정입니다!","강아지랑 함께라 더 즐거웠어요 🐶",
           "완전 최애 장소가 됐어요!","반려견 성지 인정입니다!","바로 후기 남기고 싶었어요 ㅎㅎ"]
NEU_END = ["전반적으로 만족스러웠어요.","또 방문할 것 같아요.","나쁘지 않은 곳이에요.","기회되면 다시 올게요.",
           "반려견 동반 가능한 게 장점이에요.","무난한 방문이었어요.","기대치에 딱 맞았어요.","평균 이상은 됩니다."]
NEG_END = ["공간이 조금 더 넓었으면 좋겠어요.","대형견 동반 여부는 미리 확인하세요.","주말엔 붐비니 평일 추천해요.",
           "주차가 좀 불편했어요.","가격 대비 아쉬운 부분이 있었어요.","안내 표지판이 부족했어요.",
           "반려동물 시설이 더 보강되면 좋겠어요."]

EMOJI = ["🐾🐶❤️","🌿☀️🐕","🏃💨🐩","📸✨🐾","🌸🌼🐶","🍖😋🐾","🌊🏖️🐕","🍃🌲🐾","🎉🥳🐶","💕🐾😊",
         "🌈☁️🐕","🍀🌿🐾","🏔️🌄🐕","🌺🌻🐾","🎀💝🐶","🦮🐾💚","🌙⭐🐕","🍁🍂🐾","❄️⛄🐶","🌱🌳🐾"]

# 자랑게시판 사진용 placeholder (실제 업로드 전 더미 이미지)
PHOTO_URLS = [f"/uploads/sample_dog_{i}.jpg" for i in range(1, 13)]


def build_review(category, rating):
    n = random.choice(PET_NAMES)
    s, w, t = random.choice(SEASONS), random.choice(WEATHERS), random.choice(TIMES)
    c, tr = random.choice(COMPANIONS), random.choice(TRANSPORT)
    desc = random.choice(PLACE_DESC.get(category, DEFAULT_DESC))
    react = random.choice(PET_REACT).format(n=n)
    fac = random.choice(FACILITY)
    em = random.choice(EMOJI)

    if rating == 5:
        opener = random.choice([
            f"{s}에 {w} {t} {c} {tr} 다녀왔어요. {desc} 곳이라 너무 좋았어요!",
            f"{t} {c} 방문했는데 기대 이상이었어요. {desc} 분위기에 완전 반했습니다.",
            f"{w} {tr} {t} 갔는데 정말 대만족! {desc} 공간이라 강아지도 편해 보였어요.",
            f"드디어 다녀왔어요! {desc} 곳이라 소문 듣고 {c} 왔는데 소문보다 훨씬 좋네요.",
            f"SNS에서 보고 {c} 방문했어요. {desc} 분위기가 사진보다 실제로 더 좋았어요!",
        ])
        detail = random.choice([
            f"{react}. {fac}. {random.choice(POS_END)} {em}",
            f"{fac} {react}. {random.choice(POS_END)} {em}",
            f"{react}. {fac}. {em} {random.choice(POS_END)}",
        ])
    elif rating == 4:
        opener = random.choice([
            f"{t} {c} 방문했어요. 전반적으로 만족스러운 {desc} 곳이었어요.",
            f"{w} {tr} {t} 갔어요. {desc} 분위기가 마음에 들었어요.",
            f"{s}에 {c} 다녀왔는데 꽤 좋았어요. {desc} 곳이라 강아지도 좋아했어요.",
            f"처음 방문했는데 {desc} 공간이 인상적이었어요. {t} 여유롭게 즐겼어요.",
        ])
        detail = random.choice([
            f"{react}. {fac} {random.choice(POS_END + NEU_END)}",
            f"{fac} {react}. {random.choice(NEU_END)}",
            f"{react}. {random.choice(NEU_END)}",
        ])
    elif rating == 3:
        opener = random.choice([
            f"{t} {c} 방문했어요. 나쁘진 않았는데 기대보다는 평범했어요.",
            f"{tr} {t} 갔는데 무난했어요. 반려동물 동반 가능한 게 장점이에요.",
            f"{w} 방문했어요. {desc} 편이긴 한데 아쉬운 점도 있었어요.",
        ])
        detail = random.choice([
            f"{react}. {random.choice(NEU_END)}",
            f"{fac} {random.choice(NEU_END)}",
        ])
    else:
        opener = random.choice([
            f"{t} 방문했는데 아쉬웠어요.","기대하고 갔는데 실망스러운 부분이 있었어요.",
            f"{c} 갔는데 생각보다 불편했어요.",
        ])
        detail = random.choice([
            f"{random.choice(NEG_END)} 다음엔 더 나아지길 바랍니다.",
            f"{react}. 그래도 {random.choice(NEG_END)}",
        ])
    return f"{opener} {detail}"


def make_nicknames(n):
    used, out = set(), []
    while len(out) < n:
        nk = random.choice(FIRST) + random.choice(SECOND) + random.choice(SUFFIX)
        if nk not in used:
            used.add(nk); out.append(nk)
    return out


def main():
    print("🚀 가상 데이터 생성 시작!")
    print("=" * 55)
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # 장소 확인
    cur.execute("SELECT place_id, category FROM kto_pet_places")
    places = cur.fetchall()
    if not places:
        print("❌ kto_pet_places가 비어있어요. 먼저 2_import_and_enrich.py를 실행하세요.")
        return
    print(f"📍 장소 {len(places):,}개 확인")

    # 초기화
    print("🗑️  기존 가상 데이터 초기화...")
    cur.execute("TRUNCATE place_reviews RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE user_pet_map  RESTART IDENTITY CASCADE")
    cur.execute("DELETE FROM pets")
    cur.execute("DELETE FROM app_users")
    conn.commit()

    # 유저 (비밀번호는 'password123'을 bcrypt 해시한 고정값 - 데모용)
    import bcrypt
    demo_hash = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    print(f"👤 유저 {USER_COUNT:,}명 생성...")
    nicks = make_nicknames(USER_COUNT)
    user_batch = [(nicks[i], f"petlover{i+1}@pettrip.com", demo_hash) for i in range(USER_COUNT)]
    cur.executemany("INSERT INTO app_users (nickname,email,password_hash) VALUES (%s,%s,%s)", user_batch)
    conn.commit()
    cur.execute("SELECT user_id FROM app_users ORDER BY user_id")
    user_ids = [r[0] for r in cur.fetchall()]

    # 펫
    print(f"🐶 반려동물 {PET_COUNT:,}마리 생성...")
    pet_batch = [(random.choice(PET_NAMES), random.choice(BREEDS), round(random.uniform(2,45),1))
                 for _ in range(PET_COUNT)]
    cur.executemany("INSERT INTO pets (pet_name,pet_breed,pet_weight) VALUES (%s,%s,%s)", pet_batch)
    conn.commit()
    cur.execute("SELECT pet_id FROM pets ORDER BY pet_id")
    pet_ids = [r[0] for r in cur.fetchall()]

    # 매핑
    print("🔗 유저-펫 매핑 생성...")
    mapping = set()
    shuffled = pet_ids[:USER_COUNT]; random.shuffle(shuffled)
    for u, p in zip(user_ids, shuffled):
        mapping.add((u, p))
    for p in pet_ids[USER_COUNT:]:
        mapping.add((random.choice(user_ids), p))
    for _ in range(1000):   # 공동소유
        mapping.add((random.choice(user_ids), random.choice(pet_ids)))
    cur.executemany("INSERT INTO user_pet_map (user_id,pet_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", list(mapping))
    conn.commit()
    print(f"   매핑 {len(mapping):,}쌍 완료")

    # 리뷰
    print(f"📝 리뷰 생성 (장소당 1~39개)...")
    total = 0; batch = []
    for idx, (pid, cat) in enumerate(places):
        for _ in range(random.randint(1, 39)):
            rating = random.choices([1,2,3,4,5], weights=[2,3,10,35,50])[0]
            comment = build_review(cat or "관광지", rating)
            photo = random.choice(PHOTO_URLS) if random.random() < PHOTO_RATIO else None
            batch.append((pid, random.choice(user_ids), rating, comment, photo))
        if len(batch) >= 1000:
            cur.executemany(
                "INSERT INTO place_reviews (place_id,user_id,rating,comment,photo_url) VALUES (%s,%s,%s,%s,%s)", batch)
            conn.commit(); total += len(batch); batch = []
        if (idx+1) % 1000 == 0:
            print(f"   ⏳ {idx+1:,}/{len(places):,} 장소 | 리뷰 {total:,}개")
    if batch:
        cur.executemany(
            "INSERT INTO place_reviews (place_id,user_id,rating,comment,photo_url) VALUES (%s,%s,%s,%s,%s)", batch)
        conn.commit(); total += len(batch)

    cur.close(); conn.close()
    print("=" * 55)
    print(f"🎉 완료!")
    print(f"   👤 유저 {USER_COUNT:,} / 🐶 펫 {PET_COUNT:,} / 🔗 매핑 {len(mapping):,} / 📝 리뷰 {total:,}")
    print(f"   (데모 계정 비밀번호: 모두 'password123')")
    print("=" * 55)


if __name__ == "__main__":
    main()