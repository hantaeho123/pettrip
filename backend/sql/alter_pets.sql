-- ════════════════════════════════════════════════════════════════
--  PetTrip 스키마 업데이트: 공동등록 초대코드 + 강아지 사진
--  기존 테이블에 컬럼 추가 (데이터 유지)
--
--  실행: psql -U postgres -d pettrip -f sql/alter_pets.sql
-- ════════════════════════════════════════════════════════════════

-- 1. 초대코드: 랜덤 6자리, 다른 사람이 이 코드로 공동 소유자 등록
ALTER TABLE pets ADD COLUMN IF NOT EXISTS invite_code VARCHAR(10) UNIQUE;

-- 2. 강아지 프로필 사진
ALTER TABLE pets ADD COLUMN IF NOT EXISTS photo_url TEXT;
