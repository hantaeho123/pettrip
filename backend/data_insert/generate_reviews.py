import random
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# ══════════════════════════════════════════════════════════════════════
#  재료 풀
# ══════════════════════════════════════════════════════════════════════

NICKNAMES = [
    "초코아빠","벨라맘","콩이네","두부댁","루이엄마","해피아빠","뭉치네","나비맘",
    "보리아빠","코코네","몽이댁","땅콩아빠","솜이맘","구름이네","달이아빠","별이맘",
    "하루네","봄이댁","여름이맘","가을이아빠","겨울이네","복이맘","덕이아빠","순이네",
    "돌이댁","삼순이맘","방울이아빠","노을이네","새벽이맘","햇살이댁","바람이네",
    "이슬이맘","소나기아빠","천둥이네","번개맘","무지개아빠","은하네","별빛이맘",
    "새싹이아빠","꽃잎이네","단풍이맘","눈꽃이아빠","서리네","안개맘","이랑이아빠",
    "물결이네","파도맘","모래아빠","하늘이네","구름맘",
]

EMAILS = [f"petlover{i}@pettrip.com" for i in range(1, 51)]

BREEDS = [
    "골든리트리버","말티즈","포메라니안","시바이누","웰시코기","비숑프리제","토이푸들",
    "치와와","닥스훈트","보더콜리","래브라도리트리버","허스키","진돗개","불독","비글",
    "슈나우저","요크셔테리어","사모예드","아키타","셰퍼드","코커스패니얼","달마시안",
    "그레이하운드","바셋하운드","퍼그","샤페이","차우차우","말라뮤트","도베르만","삽살개",
]

PET_NAMES = [
    "초코","콩이","두부","루이","벨라","해피","뭉치","나비","보리","코코","몽이","땅콩",
    "솜이","구름","달이","별이","하루","봄이","여름","가을","겨울","복이","방울","노을",
    "새벽","햇살","바람","이슬","무지개","은하","별빛","새싹","꽃잎","단풍","눈꽃",
]

SEASONS   = ["봄","여름","가을","겨울"]
WEATHERS  = ["맑은 날","흐린 날","비 온 뒤","선선한 날","더운 날","쌀쌀한 날","눈 오는 날"]
TIMES     = ["오전에","점심때","오후에","저녁 무렵","주말에","평일 아침에","연휴에","황금연휴에"]
COMPANIONS= ["강아지랑 둘이서","가족이랑 함께","친구랑 같이","커플로","혼자 강아지 데리고","반려인 모임으로"]
TRANSPORT = ["차 타고","대중교통으로","자전거 타고","걸어서","킥보드 타고"]

PLACE_DESC = {
    "카페": ["아늑한","탁 트인 테라스가 있는","아기자기한","빈티지 감성의","모던한",
              "숲속 느낌의","한옥 스타일의","루프탑이 멋진","뷰가 끝내주는","조용하고 한적한",
              "인스타 감성 넘치는","원목 인테리어의","따뜻한 조명의","세련된","감성적인"],
    "식당": ["현지인 맛집으로 소문난","양이 푸짐한","깔끔하고 정갈한","가성비 최고인",
              "분위기 있는","전통 느낌의","캐주얼한","고급스러운","아늑한","활기찬",
              "정성이 느껴지는","사장님이 친절한","오래된 단골 느낌의","신선한 재료를 쓰는"],
    "숙소": ["아늑하고 깨끗한","넓은 마당이 있는","자연 속에 있는","리조트 같은",
              "감성 넘치는","조용하고 프라이빗한","바다가 보이는","산 속의","도심 속 오아시스 같은",
              "반려견 전용 시설이 완비된","풀빌라 같은","캠핑 느낌의","한옥 느낌의"],
    "공원": ["넓고 쾌적한","잔디가 잘 깔린","나무 그늘이 많은","산책로가 잘 정비된",
              "탁 트인","호수가 있는","꽃이 만발한","단풍이 드는","눈 덮인","시원한 바람이 부는",
              "반려동물 전용 구역이 있는","잘 관리된","자연 그대로의"],
    "관광지": ["역사 깊은","경치가 아름다운","포토스팟이 많은","숨겨진 명소인",
                "접근성이 좋은","현지 감성 넘치는","자연친화적인","웅장한","아기자기한",
                "계절마다 다른 매력의","야경이 멋진","일출/일몰 명소인"],
}
DEFAULT_DESC = ["분위기 있는","깔끔한","넓은","아늑한","쾌적한","매력적인","독특한"]

PET_REACTIONS = [
    "{name}이(가) 꼬리를 쉴 새 없이 흔들었어요",
    "{name}이(가) 냄새 맡느라 여념이 없었어요 ㅋㅋ",
    "{name}이(가) 다른 강아지들이랑 금방 친해졌어요",
    "{name}이(가) 엄청 신나서 뛰어다녔어요",
    "{name}이(가) 낯선 환경인데도 금방 적응했어요",
    "{name}이(가) 처음엔 긴장했는데 곧 편안해했어요",
    "{name}이(가) 간식 냄새 맡고 눈을 반짝반짝했어요",
    "{name}이(가) 산책하면서 완전 행복해 보였어요",
    "{name}이(가) 돌아가기 싫었는지 한참 버텼어요 ㅎㅎ",
    "{name}이(가) 지쳐서 돌아오는 차에서 바로 잠들었어요",
    "{name}이(가) 풀밭에서 데굴데굴 구르며 놀았어요",
    "{name}이(가) 직원분께 애교 부리면서 간식 받아먹었어요",
    "{name}이(가) 사진 찍을 때마다 포즈 취해줬어요 ㅋㅋ",
    "{name}이(가) 다른 손님들한테 인기 폭발이었어요",
    "{name}이(가) 강아지 친구 사귀고 놀더니 지쳐버렸어요",
    "{name}이(가) 바닥 냄새 맡으면서 탐정처럼 돌아다녔어요",
    "{name}이(가) 처음 보는 환경에 두리번거렸는데 금방 즐거워했어요",
    "{name}이(가) 밥도 잘 먹고 산책도 실컷 했어요",
]

FACILITY_COMMENTS = [
    "물그릇을 따로 갖다주셔서 감동이었어요",
    "강아지 전용 간식도 팔아서 너무 좋았어요",
    "펫 전용 입구가 따로 있어서 편했어요",
    "야외 테라스가 넓어서 여유롭게 앉을 수 있었어요",
    "강아지 목줄 걸이가 곳곳에 있어서 편리했어요",
    "화장실이 깔끔하게 관리되고 있었어요",
    "주차 공간이 넉넉해서 편하게 왔어요",
    "대형견도 편하게 이동할 수 있는 공간이라 좋았어요",
    "반려동물 입장 안내가 잘 되어 있어서 처음 가도 헷갈리지 않았어요",
    "강아지 배변 봉투가 비치되어 있어서 편리했어요",
    "포토존이 있어서 예쁜 사진 많이 찍었어요",
    "실내도 강아지 동반 가능해서 날씨 걱정 없었어요",
    "직원분들이 강아지를 무서워하지 않아서 좋았어요",
    "다양한 견종의 강아지들이 사이좋게 놀 수 있었어요",
    "산책로가 잘 정비되어 있어서 발바닥 걱정 없었어요",
    "반려견 전용 놀이 공간이 따로 마련되어 있었어요",
    "그늘이 충분해서 더운 날에도 괜찮았어요",
    "음식이 맛있는데 강아지까지 반겨주니 더할 나위 없었어요",
    "입장료가 없어서 부담 없이 다녀올 수 있었어요",
    "매장이 넓어서 강아지가 부딪힐 걱정이 없었어요",
]

POSITIVE_ENDINGS = [
    "다음에 꼭 또 올게요! 🐾",
    "강아지 키우는 분들께 강력 추천드려요!",
    "반려견 동반 여행지로 최고예요 ✨",
    "단골이 될 것 같아요 ㅎㅎ",
    "주변 반려인들한테도 다 알려줬어요!",
    "사진도 잘 나오고 강아지도 행복해했어요 📸",
    "멀리서 왔는데 왔을 가치가 충분했어요!",
    "이런 곳이 더 많아졌으면 좋겠어요",
    "반려동물 친화적인 곳 찾는다면 바로 여기예요!",
    "오래오래 운영해주세요 🙏",
    "재방문 100% 예정입니다!",
    "강아지랑 함께라서 더 즐거웠어요 🐶",
    "완전 최애 장소가 됐어요!",
    "이 정도면 반려견 성지 인정이에요!",
    "포스팅하고 싶어서 바로 글 쓰고 있어요 ㅎㅎ",
]

NEUTRAL_ENDINGS = [
    "전반적으로 만족스러웠어요.",
    "또 방문할 것 같아요.",
    "나쁘지 않은 곳이에요.",
    "기회가 되면 다시 올 것 같아요.",
    "반려견 동반 가능한 곳이 많지 않아서 감사해요.",
    "무난한 방문이었어요.",
    "기대치에 딱 맞는 곳이었어요.",
    "평균 이상은 되는 곳이에요.",
]

NEGATIVE_ENDINGS = [
    "공간이 조금 더 넓었으면 좋겠어요.",
    "대형견 동반 가능 여부는 미리 확인하고 가세요.",
    "주말엔 좀 붐비니 평일 방문을 추천해요.",
    "주차가 좀 불편했어요.",
    "가격 대비 아쉬운 부분이 있었어요.",
    "안내 표지판이 더 잘 되어 있으면 좋겠어요.",
    "반려동물 전용 시설이 조금 더 보강되면 좋을 것 같아요.",
]

EMOJI_SETS = [
    "🐾🐶❤️","🌿☀️🐕","🏃💨🐩","📸✨🐾","🌸🌼🐶",
    "🍖😋🐾","🌊🏖️🐕","🍃🌲🐾","🎉🥳🐶","💕🐾😊",
    "🌈☁️🐕","🍀🌿🐾","🏔️🌄🐕","🌺🌻🐾","🎀💝🐶",
    "🦮🐾💚","🌙⭐🐕","🍁🍂🐾","❄️⛄🐶","🌱🌳🐾",
]


# ══════════════════════════════════════════════════════════════════════
#  리뷰 문장 조합기
# ══════════════════════════════════════════════════════════════════════

def build_review(place_name, category, rating):
    pet_name  = random.choice(PET_NAMES)
    season    = random.choice(SEASONS)
    weather   = random.choice(WEATHERS)
    time_     = random.choice(TIMES)
    companion = random.choice(COMPANIONS)
    transport = random.choice(TRANSPORT)
    desc_pool = PLACE_DESC.get(category, DEFAULT_DESC)
    desc      = random.choice(desc_pool)
    reaction  = random.choice(PET_REACTIONS).format(name=pet_name)
    facility  = random.choice(FACILITY_COMMENTS)
    emoji     = random.choice(EMOJI_SETS)

    # ── 오프너 (상황 설명) ──────────────────────────────────────────
    openers_5 = [
        f"{season}에 {weather} {time_} {companion} {transport} 다녀왔어요. {desc} 곳이라 너무 좋았어요!",
        f"{time_} {companion} 방문했는데 기대 이상이었어요. {desc} 분위기에 완전 반했습니다.",
        f"{weather} {transport} {time_} 갔는데 정말 대만족이에요! {desc} 공간이라 강아지도 편해보였어요.",
        f"{season} 여행으로 {companion} 찾아갔어요. {desc} 곳이었고 분위기 너무 좋았습니다!",
        f"드디어 다녀왔어요! {desc} 곳이라는 소문 듣고 {companion} 왔는데 소문보다 훨씬 좋네요.",
        f"오래 벼르다가 {season}에 드디어 왔어요. {transport} 왔는데 올 가치가 충분했어요!",
        f"SNS에서 보고 {companion} 방문했어요. {desc} 분위기가 사진보다 실제로 더 좋았어요!",
    ]
    openers_4 = [
        f"{time_} {companion} 방문했어요. 전반적으로 만족스러운 {desc} 곳이었습니다.",
        f"{weather} {transport} {time_} 갔어요. {desc} 분위기가 마음에 들었어요.",
        f"{season}에 {companion} 다녀왔는데 꽤 좋았어요. {desc} 곳이라서 강아지도 좋아했어요.",
        f"처음 방문했는데 {desc} 공간이 인상적이었어요. {time_} 가서 여유롭게 즐겼어요.",
        f"{companion} {time_} 방문했어요. 기대했던 것과 비슷하게 좋았어요.",
    ]
    openers_3 = [
        f"{time_} {companion} 방문했어요. 나쁘진 않았는데 기대보다는 평범했어요.",
        f"{transport} {time_} 갔는데 무난했어요. 반려동물 동반 가능한 게 장점이에요.",
        f"{weather} 방문했어요. {desc} 편이긴 했는데 아쉬운 점도 있었어요.",
        f"{companion} 갔다 왔어요. 보통 수준이었는데 강아지 데려갈 수 있어서 다행이에요.",
    ]
    openers_low = [
        f"{time_} 방문했는데 아쉬웠어요.",
        f"기대하고 갔는데 실망스러운 부분이 있었어요.",
        f"{companion} 갔는데 생각보다 불편했어요.",
        f"리뷰 보고 갔는데 제 기대치와는 달랐어요.",
    ]

    # ── 디테일 문장 ─────────────────────────────────────────────────
    details_high = [
        f"{reaction}. {facility}. {random.choice(POSITIVE_ENDINGS)} {emoji}",
        f"{facility} {reaction}. {random.choice(POSITIVE_ENDINGS)} {emoji}",
        f"{reaction}. {facility}. {emoji} {random.choice(POSITIVE_ENDINGS)}",
        f"{facility} {emoji} {reaction}. {random.choice(POSITIVE_ENDINGS)}",
    ]
    details_mid = [
        f"{reaction}. {facility} {random.choice(NEUTRAL_ENDINGS)}",
        f"{facility} {reaction}. {random.choice(NEUTRAL_ENDINGS)}",
        f"{reaction}. {random.choice(NEUTRAL_ENDINGS)}",
    ]
    details_low = [
        f"{random.choice(NEGATIVE_ENDINGS)} 다음엔 더 나아지길 바랍니다.",
        f"{reaction}. 그래도 {random.choice(NEGATIVE_ENDINGS)}",
        f"{random.choice(NEGATIVE_ENDINGS)} 개선이 필요해 보여요.",
    ]

    if rating == 5:
        return f"{random.choice(openers_5)} {random.choice(details_high)}"
    elif rating == 4:
        return f"{random.choice(openers_4)} {random.choice(details_high + details_mid)}"
    elif rating == 3:
        return f"{random.choice(openers_3)} {random.choice(details_mid)}"
    else:
        return f"{random.choice(openers_low)} {random.choice(details_low)}"


# ══════════════════════════════════════════════════════════════════════
#  DB 유저/펫 생성
# ══════════════════════════════════════════════════════════════════════

def setup_users_and_pets(cur, conn):
    print("👤 유저 및 반려동물 데이터 생성 중...")
    user_ids = []
    for nick, email in zip(NICKNAMES, EMAILS):
        cur.execute("""
            INSERT INTO app_users (nickname, email)
            VALUES (%s, %s)
            ON CONFLICT (email) DO UPDATE SET nickname = EXCLUDED.nickname
            RETURNING user_id
        """, (nick, email))
        user_ids.append(cur.fetchone()[0])

    pet_ids = []
    for _ in range(len(NICKNAMES)):
        cur.execute("""
            INSERT INTO pets (pet_name, pet_breed, pet_weight)
            VALUES (%s, %s, %s) RETURNING pet_id
        """, (random.choice(PET_NAMES), random.choice(BREEDS),
               round(random.uniform(2.0, 38.0), 1)))
        pet_ids.append(cur.fetchone()[0])

    for uid, pid in zip(user_ids, pet_ids):
        cur.execute("INSERT INTO user_pet_map (user_id, pet_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (uid, pid))
    for _ in range(10):
        cur.execute("INSERT INTO user_pet_map (user_id, pet_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (random.choice(user_ids), random.choice(pet_ids)))

    conn.commit()
    print(f"✅ 유저 {len(user_ids)}명, 반려동물 {len(pet_ids)}마리 생성 완료")
    return user_ids


# ══════════════════════════════════════════════════════════════════════
#  리뷰 생성
# ══════════════════════════════════════════════════════════════════════

def generate_reviews(cur, conn, user_ids, places):
    print(f"\n📝 {len(places)}개 장소 리뷰 생성 시작...")
    total = 0
    batch = []

    for idx, (place_id, place_name, category) in enumerate(places):
        count = random.randint(1, 39)
        for _ in range(count):
            rating  = random.choices([1,2,3,4,5], weights=[2,3,10,35,50], k=1)[0]
            comment = build_review(place_name or "이곳", category or "", rating)
            batch.append((place_id, random.choice(user_ids), rating, comment))

        if len(batch) >= 500:
            cur.executemany(
                "INSERT INTO place_reviews (place_id, user_id, rating, comment) VALUES (%s,%s,%s,%s)",
                batch)
            conn.commit()
            total += len(batch)
            batch  = []

        if (idx + 1) % 1000 == 0:
            print(f"  ⏳ {idx+1}/{len(places)} ({(idx+1)/len(places)*100:.0f}%) | 누적 {total:,}개")

    if batch:
        cur.executemany(
            "INSERT INTO place_reviews (place_id, user_id, rating, comment) VALUES (%s,%s,%s,%s)",
            batch)
        conn.commit()
        total += len(batch)

    return total


# ══════════════════════════════════════════════════════════════════════
#  메인
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 다양한 리뷰 더미 데이터 생성 시작!")
    print("=" * 55)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    cur.execute("SELECT place_id, place_name, category FROM kto_pet_places")
    places = cur.fetchall()
    print(f"📍 총 {len(places)}개 장소 확인")

    # 기존 데이터 초기화
    print("🗑️  기존 더미 데이터 초기화 중...")
    cur.execute("TRUNCATE TABLE place_reviews RESTART IDENTITY CASCADE")
    cur.execute("TRUNCATE TABLE user_pet_map  RESTART IDENTITY CASCADE")
    cur.execute("DELETE FROM pets")
    cur.execute("DELETE FROM app_users")
    conn.commit()

    user_ids      = setup_users_and_pets(cur, conn)
    total_reviews = generate_reviews(cur, conn, user_ids, places)

    cur.close()
    conn.close()

    avg = total_reviews // len(places) if places else 0
    print("\n" + "=" * 55)
    print(f"🎉 완료!")
    print(f"   📍 장소  : {len(places):,}개")
    print(f"   👤 유저  : {len(user_ids)}명")
    print(f"   📝 리뷰  : {total_reviews:,}개")
    print(f"   📊 평균  : 장소당 약 {avg}개")
    print("=" * 55)