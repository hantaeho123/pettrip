"""
main.py
PetTrip FastAPI 백엔드 진입점

- CORS 설정 (프론트엔드 localhost:3000 허용)
- 업로드된 이미지 정적 서빙 (/uploads)
- 라우터 등록: auth, places, reviews, pets, stats

실행: uvicorn main:app --reload
문서: http://localhost:8000/docs (Swagger UI)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import engine, Base
from app.routers import auth, places, reviews, pets, stats

# 모델 기준으로 테이블이 없으면 생성 (보통은 ddl.sql로 생성하지만 안전장치)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PetTrip API",
    description="반려동물 동반 여행 지도 플랫폼 백엔드",
    version="1.0.0",
)

# ── CORS: 프론트엔드에서의 요청 허용 ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 업로드 이미지 정적 서빙 ────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── 라우터 등록 ────────────────────────────────────────────────────
app.include_router(auth.router,    prefix="/api/auth",    tags=["인증"])
app.include_router(places.router,  prefix="/api/places",  tags=["장소"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["리뷰"])
app.include_router(pets.router,    prefix="/api/pets",    tags=["반려동물"])
app.include_router(stats.router,   prefix="/api/stats",   tags=["통계"])


@app.get("/")
def root():
    return {"message": "PetTrip API is running 🐾", "docs": "/docs"}
