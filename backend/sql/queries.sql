-- ════════════════════════════════════════════════════════════════════
--  PetTrip 서비스 기능별 주요 SQL 쿼리 모음 (DML)
--  보고서 [SQL문] 섹션 + 가산점 요소(VIEW/TRIGGER/ROLLUP) 시연용
-- ════════════════════════════════════════════════════════════════════


-- ────────────────────────────────────────────────────────────────────
-- 기능 1. [지도 탐색] 특정 카테고리의 동반 가능 장소 검색
--         지도 화면 좌표 범위 내 + 카테고리 필터
-- ────────────────────────────────────────────────────────────────────
SELECT place_id, place_name, latitude, longitude, pet_policy
FROM kto_pet_places
WHERE category = '카페'
  AND latitude  BETWEEN 37.2 AND 37.6
  AND longitude BETWEEN 126.8 AND 127.2;


-- ────────────────────────────────────────────────────────────────────
-- 기능 2. [장소 상세] VIEW를 이용한 평균 평점·리뷰 수 즉시 조회
--         (가산점 요소 - VIEW 활용)
-- ────────────────────────────────────────────────────────────────────
SELECT * FROM vw_place_detail_stats WHERE place_id = 'KTO_001';

-- 특정 장소의 리뷰 목록 + 작성자 닉네임 (최신순)
SELECT
    p.place_name AS "장소명",
    u.nickname   AS "작성자",
    r.rating     AS "평점",
    r.comment    AS "리뷰내용",
    r.photo_url  AS "사진",
    r.created_at AS "작성일"
FROM place_reviews r
JOIN kto_pet_places p ON r.place_id = p.place_id
JOIN app_users      u ON r.user_id  = u.user_id
WHERE r.place_id = 'KTO_001'
ORDER BY r.created_at DESC;


-- ────────────────────────────────────────────────────────────────────
-- 기능 3. [개인화 필터] 대형견(25kg)이 실내 동반 가능한 카페만 필터링
--         JOIN + 비교 연산 + HAVING (평점 4.0 이상)
-- ────────────────────────────────────────────────────────────────────
SELECT p.place_name, p.category, p.address
FROM kto_pet_places p
JOIN place_reviews  r ON p.place_id = r.place_id
WHERE p.max_weight_limit >= 25.0
  AND p.is_indoor_allowed = TRUE
  AND p.category = '카페'
GROUP BY p.place_id
HAVING AVG(r.rating) >= 4.0;


-- ────────────────────────────────────────────────────────────────────
-- 기능 4. [멍트립 다이어리] 같은 펫을 공동 소유한 유저들의 통합 방문 이력
--         user_pet_map(N:M) 테이블 4개 JOIN
-- ────────────────────────────────────────────────────────────────────
SELECT DISTINCT
    pt.pet_name  AS "반려견",
    p.place_name AS "방문장소",
    r.rating     AS "평점",
    u.nickname   AS "작성자"
FROM pets pt
JOIN user_pet_map m1 ON pt.pet_id  = m1.pet_id          -- 펫 → 모든 소유자
JOIN app_users    u  ON m1.user_id = u.user_id
JOIN place_reviews r ON u.user_id  = r.user_id          -- 소유자 → 작성 리뷰
JOIN kto_pet_places p ON r.place_id = p.place_id
WHERE pt.pet_id = 1
ORDER BY r.rating DESC;


-- ────────────────────────────────────────────────────────────────────
-- 기능 5. [견종별 랭킹] 특정 견종 견주들이 4점 이상 준 인기 장소 순위
-- ────────────────────────────────────────────────────────────────────
SELECT
    p.place_name,
    p.category,
    ROUND(AVG(r.rating), 1) AS avg_rating,
    COUNT(r.review_id)      AS review_count
FROM place_reviews r
JOIN kto_pet_places p ON r.place_id = p.place_id
JOIN user_pet_map   m ON r.user_id  = m.user_id
JOIN pets          pt ON m.pet_id   = pt.pet_id
WHERE pt.pet_breed = '웰시코기'
  AND r.rating    >= 4
GROUP BY p.place_id, p.place_name, p.category
ORDER BY avg_rating DESC, review_count DESC
LIMIT 10;


-- ────────────────────────────────────────────────────────────────────
-- 기능 6. [회원 탈퇴] ON DELETE CASCADE 시연
--         유저 삭제 시 해당 유저의 리뷰·펫 매핑이 자동 삭제됨
-- ────────────────────────────────────────────────────────────────────
DELETE FROM app_users WHERE user_id = 1;


-- ════════════════════════════════════════════════════════════════════
--  [가산점 요소 ③] ROLLUP (OLAP)
--  시설 카테고리 × 야외 마당 유무별 평점 분석 + 소계/총계 집계
-- ════════════════════════════════════════════════════════════════════
SELECT
    COALESCE(p.category, '전체 총계')                       AS "시설 카테고리",
    COALESCE(CAST(p.has_outdoor_yard AS VARCHAR), '분류 소계') AS "야외 마당 유무",
    ROUND(AVG(r.rating), 2)                                AS "평균 평점",
    COUNT(r.review_id)                                     AS "총 누적 리뷰 수"
FROM kto_pet_places p
JOIN place_reviews  r ON p.place_id = r.place_id
GROUP BY ROLLUP(p.category, p.has_outdoor_yard)
ORDER BY p.category, p.has_outdoor_yard;
