-- ════════════════════════════════════════════════════════════════════
--  PetTrip 데이터베이스 스키마 (DDL)
--  2026-1 데이터베이스 프로젝트 / 한태호 202021190
--
--  실행 순서대로 작성되어 있습니다.
--  psql -U postgres -d pettrip -f sql/ddl.sql
-- ════════════════════════════════════════════════════════════════════

-- 재실행 시 깨끗하게 초기화 (개발 편의용)
DROP VIEW     IF EXISTS vw_place_detail_stats CASCADE;
DROP TABLE    IF EXISTS place_reviews CASCADE;
DROP TABLE    IF EXISTS user_pet_map  CASCADE;
DROP TABLE    IF EXISTS pets          CASCADE;
DROP TABLE    IF EXISTS app_users     CASCADE;
DROP TABLE    IF EXISTS kto_pet_places CASCADE;


-- ────────────────────────────────────────────────────────────────────
-- 1. [실제 데이터] 한국관광공사 반려동물 동반여행 API 장소 정보
--    공공데이터포털 TourAPI의 detailPetTour / areaBasedList 응답을 저장
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE kto_pet_places (
    place_id         VARCHAR(50)  PRIMARY KEY,          -- API: contentid (장소 고유 ID)
    place_name       VARCHAR(100) NOT NULL,             -- API: title (장소명)
    category         VARCHAR(50),                       -- API: contenttypeid 변환 (카페/식당/숙소 등)
    address          VARCHAR(255),                      -- API: addr1 + addr2 (주소)
    latitude         DECIMAL(10, 7),                    -- API: mapy (위도)
    longitude        DECIMAL(10, 7),                    -- API: mapx (경도)

    -- ── 반려동물 동반 정책 (필터링 핵심 컬럼) ──────────────────────
    pet_size_limit   VARCHAR(100),                      -- API: acmpyPsblCpam (동반 가능 동물 텍스트)
    max_weight_limit DECIMAL(5, 2),                     -- [가공] 수치 비교용 최대 허용 몸무게(kg)
    pet_policy       TEXT,                              -- API: acmpyNeedMtr (동반 시 필요사항)
    pet_type_code    VARCHAR(50),                       -- API: acmpyTypeCd (동반 유형: 전용/동반가능)

    -- ── 웹 화면 표시용 추가 정보 ──────────────────────────────────
    amenities        TEXT,                              -- API: relaFrnshPrdlst (비치 품목: 배변패드, 식기 등)
    purchase_items   TEXT,                              -- API: relaPurcPrdlst (구매 품목: 간식, 사료 등)
    rental_items     TEXT,                              -- API: relaRntlPrdlst (대여 품목: 개모차, 켄넬 등)
    safety_hazards   TEXT,                              -- API: relaAcdntRiskMtr (사고 대비사항)
    extra_info       TEXT,                              -- API: etcAcmpyInfo (기타 동반 정보)
    pet_fee_info     VARCHAR(255),                      -- (예: '소형견 무료, 대형견 10,000원')
    main_image_url   TEXT,                              -- API: firstimage (대표 이미지 URL)

    -- ── 운영 정보 ─────────────────────────────────────────────────
    operating_hours  VARCHAR(255),                      -- API: usetime (영업시간)
    closed_days      VARCHAR(255),                      -- API: restdate (휴무일)
    parking_info     VARCHAR(255),                      -- API: parking (주차 정보)
    contact_number   VARCHAR(50),                       -- API: tel (연락처)
    website_url      TEXT,                              -- API: homepage (홈페이지/SNS)

    -- ── 가공 데이터 (필터링 고도화용 boolean) ─────────────────────
    is_indoor_allowed BOOLEAN DEFAULT FALSE,            -- 실내 동반 가능 여부
    has_outdoor_yard  BOOLEAN DEFAULT FALSE,            -- 야외 공간(마당) 유무

    -- ── 메타 ──────────────────────────────────────────────────────
    updated_at       TIMESTAMP DEFAULT NOW()            -- 마지막 수정 시각 (TRIGGER로 자동 갱신)
);


-- ────────────────────────────────────────────────────────────────────
-- 2. [가상 데이터] 서비스 사용자 정보 (보안 강화: 비밀번호 해시 저장)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE app_users (
    user_id       SERIAL PRIMARY KEY,
    nickname      VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,                -- bcrypt 해시된 비밀번호
    created_at    TIMESTAMP DEFAULT NOW()
);


-- ────────────────────────────────────────────────────────────────────
-- 3. [가상 데이터] 반려동물 개체 정보
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE pets (
    pet_id      SERIAL PRIMARY KEY,
    pet_name    VARCHAR(50) NOT NULL,
    pet_breed   VARCHAR(50),
    pet_weight  DECIMAL(5, 2),                         -- 몸무게(kg) - 필터링에 사용
    invite_code VARCHAR(10) UNIQUE,                    -- 공동 소유 초대코드 (6자리 랜덤)
    photo_url   TEXT                                   -- 강아지 프로필 사진 경로
);


-- ────────────────────────────────────────────────────────────────────
-- 4. [관계 매핑] 주인 ↔ 반려동물 다대다(N:M) 소유 관계
--    복합 기본키로 같은 유저가 같은 펫을 중복 등록하는 것을 방지
--    → '가족 공동 멍트립 다이어리' 시나리오의 핵심 테이블
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE user_pet_map (
    user_id INT REFERENCES app_users(user_id) ON DELETE CASCADE,
    pet_id  INT REFERENCES pets(pet_id)       ON DELETE CASCADE,
    PRIMARY KEY (user_id, pet_id)
);


-- ────────────────────────────────────────────────────────────────────
-- 5. [가상 데이터] 장소 방문 후기 및 평점
--    photo_url 컬럼으로 '반려동물 자랑하기' 사진 공유 지원
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE place_reviews (
    review_id  SERIAL PRIMARY KEY,
    place_id   VARCHAR(50) REFERENCES kto_pet_places(place_id) ON DELETE CASCADE,
    user_id    INT         REFERENCES app_users(user_id)        ON DELETE CASCADE,
    rating     INT CHECK (rating >= 1 AND rating <= 5),
    comment    TEXT,
    photo_url  TEXT,                                    -- 업로드한 반려동물 사진 경로
    created_at TIMESTAMP DEFAULT NOW()
);

-- 조회 성능을 위한 인덱스
CREATE INDEX idx_reviews_place ON place_reviews(place_id);
CREATE INDEX idx_reviews_user  ON place_reviews(user_id);
CREATE INDEX idx_places_cat    ON kto_pet_places(category);
CREATE INDEX idx_places_coord  ON kto_pet_places(latitude, longitude);


-- ════════════════════════════════════════════════════════════════════
--  [가산점 요소 ①] TRIGGER
--  장소 정보가 UPDATE 될 때마다 updated_at 컬럼을 자동으로 현재 시각으로 갱신
-- ════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER trigger_update_place_modtime
    BEFORE UPDATE ON kto_pet_places
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();


-- ════════════════════════════════════════════════════════════════════
--  [가산점 요소 ②] VIEW
--  장소 기본 정보 + 누적 리뷰 수 + 평균 평점을 통합한 뷰
--  → 장소 상세 화면에서 한 번의 SELECT로 즉시 로딩
-- ════════════════════════════════════════════════════════════════════
CREATE VIEW vw_place_detail_stats AS
SELECT
    p.place_id,
    p.place_name,
    p.category,
    p.address,
    p.latitude,
    p.longitude,
    p.max_weight_limit,
    p.is_indoor_allowed,
    p.has_outdoor_yard,
    p.main_image_url,
    COALESCE(ROUND(AVG(r.rating), 1), 0) AS average_rating,   -- 평균 평점 (리뷰 없으면 0)
    COUNT(r.review_id)                   AS total_reviews      -- 누적 리뷰 수
FROM kto_pet_places p
LEFT JOIN place_reviews r ON p.place_id = r.place_id
GROUP BY p.place_id;
