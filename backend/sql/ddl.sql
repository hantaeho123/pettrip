-- PetTrip DDL — 계획서 기준 스키마
-- 실행 순서: 1 → 2 → 3 → 4 → 5

-- 1. [실제 데이터] 한국관광공사 API 장소 정보
CREATE TABLE kto_pet_places (
    place_id   VARCHAR(50) PRIMARY KEY,
    place_name VARCHAR(100) NOT NULL,
    category   VARCHAR(50),
    latitude   DECIMAL(10, 7),
    longitude  DECIMAL(10, 7),
    pet_policy TEXT
);

-- 2. [가상 데이터] 서비스 사용자 정보
CREATE TABLE app_users (
    user_id  SERIAL PRIMARY KEY,
    nickname VARCHAR(50)  NOT NULL,
    email    VARCHAR(100) UNIQUE NOT NULL
);

-- 3. [가상 데이터] 반려동물 개체 정보
CREATE TABLE pets (
    pet_id     SERIAL PRIMARY KEY,
    pet_name   VARCHAR(50) NOT NULL,
    pet_breed  VARCHAR(50),
    pet_weight DECIMAL(5, 2)
);

-- 4. [관계 매핑] 주인 ↔ 반려동물 다대다(N:M)
--    복합 기본키로 중복 등록 방지
CREATE TABLE user_pet_map (
    user_id INT REFERENCES app_users(user_id) ON DELETE CASCADE,
    pet_id  INT REFERENCES pets(pet_id)       ON DELETE CASCADE,
    PRIMARY KEY (user_id, pet_id)
);

-- 5. [가상 데이터] 장소 방문 후기 및 평점
CREATE TABLE place_reviews (
    review_id SERIAL PRIMARY KEY,
    place_id  VARCHAR(50) REFERENCES kto_pet_places(place_id) ON DELETE CASCADE,
    user_id   INT         REFERENCES app_users(user_id)        ON DELETE CASCADE,
    rating    INT CHECK (rating >= 1 AND rating <= 5),
    comment   TEXT
);
