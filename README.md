# 🐾 PetTrip — 반려동물 맞춤형 지도 기반 관광 플랫폼

> 한국관광공사 반려동물 동반여행 API + 카카오맵으로 만드는 반려인을 위한 여행 커뮤니티

---

## 프로젝트 구조

```
pettrip/
├── backend/                  # FastAPI + PostgreSQL
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── app/
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── routers/
│   │       ├── places.py
│   │       ├── reviews.py
│   │       ├── pets.py
│   │       └── users.py
│   └── sql/
│       ├── ddl.sql           # 테이블 생성 DDL
│       └── sample_data.sql   # 더미 데이터
│
├── frontend/                 # React
│   ├── public/index.html
│   └── src/
│       ├── App.jsx
│       ├── api/index.js      # 백엔드 API 호출 함수
│       ├── components/
│       │   ├── Map/          # KakaoMap, PlacePin
│       │   ├── Sidebar/      # FilterPanel, PetProfile
│       │   ├── Place/        # PlaceList, PlaceDetail
│       │   └── Community/    # PostCard, RankingBoard
│       └── pages/
│           ├── MapPage.jsx
│           ├── CommunityPage.jsx
│           └── RankingPage.jsx
│
├── docs/
│   └── 프로젝트계획서_한태호_202021190.pdf
└── .gitignore
```

---

## 실행 방법

### 1. 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env 파일 생성 (.env.example 참고)
cp .env.example .env

# DB 초기화 (PostgreSQL 실행 후)
psql -U 유저명 -d pettrip -f sql/ddl.sql
psql -U 유저명 -d pettrip -f sql/sample_data.sql

# 서버 실행
uvicorn main:app --reload
# → http://localhost:8000/docs  (Swagger UI)
```

### 2. 프론트엔드

```bash
cd frontend
npm install

# .env 파일 생성
cp .env.example .env
# REACT_APP_KAKAO_MAP_KEY 값 입력

npm start
# → http://localhost:3000
```

---

## 사용 API

| API | 용도 |
|-----|------|
| [한국관광공사 TourAPI](https://api.visitkorea.or.kr) | 반려동물 동반 가능 장소 데이터 |
| [카카오맵 API](https://apis.map.kakao.com) | 지도 렌더링 및 마커 표시 |

---

## 기술 스택

- **Frontend**: React 18, Axios
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **외부 API**: 한국관광공사 TourAPI, 카카오맵 SDK

---

## 학번 / 이름

202021190 · 한태호
