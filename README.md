# 🐾 PetTrip — 반려동물 동반 여행 지도 플랫폼

> 2026-1 데이터베이스 프로젝트 / 한태호 (202021190)

한국관광공사 반려동물 동반여행 API와 카카오맵을 활용하여, 전국의 반려동물 동반 가능
장소를 지도에서 찾고 리뷰·자랑게시판을 공유하는 커뮤니티형 관광 플랫폼입니다.

---

## 📦 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React 18, Axios, 카카오맵 API |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Bcrypt |
| Database | PostgreSQL |
| External | 한국관광공사 TourAPI, 카카오맵 API |

---

## 🗂️ 프로젝트 구조

```
PetTrip/
├── backend/
│   ├── app/
│   │   ├── core/security.py      # bcrypt 비밀번호 해싱
│   │   ├── routers/              # auth, places, reviews, pets, stats
│   │   ├── database.py           # DB 연결
│   │   ├── models.py             # ORM 모델 (5테이블)
│   │   └── schemas.py            # Pydantic 스키마
│   ├── scripts/
│   │   ├── 1_fetch_kto_data.py       # 실제 API 수집
│   │   ├── 2_import_and_enrich.py    # CSV 적재 + 메타데이터 보강
│   │   └── 3_generate_dummy_data.py  # 가상 데이터 대량 생성
│   ├── sql/
│   │   ├── ddl.sql               # 스키마 + TRIGGER + VIEW
│   │   └── queries.sql           # 기능별 쿼리 + ROLLUP
│   ├── uploads/                  # 업로드된 리뷰 사진 저장소
│   └── main.py                   # FastAPI 진입점
└── frontend/
    ├── public/index.html         # 카카오 SDK 로드
    └── src/
        ├── components/           # Map, Auth, Sidebar, Place, Community
        ├── pages/MapPage.jsx     # 지도 탐색 메인
        ├── context/              # 로그인 상태 관리
        ├── api/                  # 백엔드 통신
        └── App.jsx               # 네비게이션 + 라우팅
```

---

## 🚀 실행 방법

### 0. 사전 준비
- PostgreSQL 설치 및 실행
- Node.js LTS 설치
- 카카오 개발자센터에서 JavaScript 키 발급 (Web 플랫폼에 `http://localhost:3000` 등록)
- 공공데이터포털에서 한국관광공사 반려동물 동반여행 API 키 발급

### 1. 데이터베이스 생성
```bash
# psql 접속 후
CREATE DATABASE pettrip;
```

### 2. 백엔드 설정
```bash
cd backend
pip install -r requirements.txt

# .env 파일 생성 (.env.example 복사 후 수정)
cp .env.example .env
# DATABASE_URL, KTO_API_KEY 입력

# 스키마 생성 (테이블 + TRIGGER + VIEW)
psql -U postgres -d pettrip -f sql/ddl.sql
```

### 3. 데이터 적재 (순서대로)
```bash
# ① 실제 장소 데이터 적재 (제공된 CSV 사용)
python scripts/2_import_and_enrich.py data.txt

#   또는 실제 API에서 새로 수집하려면:
#   python scripts/1_fetch_kto_data.py

# ② 가상 데이터 생성 (유저 5천 / 펫 6천 / 리뷰 약 19만)
python scripts/3_generate_dummy_data.py
```

### 4. 백엔드 실행
```bash
uvicorn main:app --reload
# → http://localhost:8000  (API 문서: http://localhost:8000/docs)
```

### 5. 프론트엔드 실행
```bash
cd frontend
npm install

# .env 파일 생성
cp .env.example .env
# REACT_APP_KAKAO_MAP_KEY 입력

npm start
# → http://localhost:3000
```

---

## ✨ 주요 기능

1. **지도 기반 장소 탐색** — 전국 지도에서 카테고리별 마커 표시, 마커 클릭 시 장소명 라벨 토글(여러 개 고정 가능)
2. **상세 정보 조회** — 동반 가능 크기, 필요사항, 시설, 운영시간 등. 검색 시 해당 위치로 이동/확대
3. **회원가입 / 로그인** — bcrypt 암호화. 리뷰·계정 삭제 지원
4. **커뮤니티 (리뷰/자랑하기)** — 별점 + 반려동물 사진 업로드
5. **멍트립 다이어리** — 공동 소유한 반려견의 통합 방문 이력 (N:M)
6. **반려견 맞춤 추천** — 등록한 펫의 몸무게 기준 입장 가능 장소 필터링
7. **견종별 인기 랭킹** — 같은 견종 견주들의 고평점 장소 집계

---

## 🎯 데이터베이스 가산점 요소

- **TRIGGER**: 장소 정보 수정 시 `updated_at` 자동 갱신
- **VIEW**: `vw_place_detail_stats` — 평균 평점·리뷰 수 통합 조회
- **ROLLUP (OLAP)**: 카테고리 × 야외마당 유무별 평점 분석 (소계/총계)

---

