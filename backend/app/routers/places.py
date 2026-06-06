from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.PlaceOut])
def get_places(
    category:   Optional[str]   = Query(None, description="카테고리 필터 (카페, 식당, 숙소, 공원)"),
    search:     Optional[str]   = Query(None, description="가게명 또는 지역명으로 검색"),
    min_lat:    Optional[float]  = Query(None),
    max_lat:    Optional[float]  = Query(None),
    min_lng:    Optional[float]  = Query(None),
    max_lng:    Optional[float]  = Query(None),
    db: Session = Depends(get_db)
):
    """지도 화면 좌표 범위 + 카테고리 필터 + 검색으로 장소 목록 반환"""
    q = db.query(models.KtoPetPlace)
    if category:
        q = q.filter(models.KtoPetPlace.category == category)
    if search:
        search_term = f"%{search}%"
        q = q.filter(models.KtoPetPlace.place_name.ilike(search_term))
    if min_lat and max_lat:
        q = q.filter(models.KtoPetPlace.latitude.between(min_lat, max_lat))
    if min_lng and max_lng:
        q = q.filter(models.KtoPetPlace.longitude.between(min_lng, max_lng))
    return q.all()


@router.get("/{place_id}", response_model=schemas.PlaceOut)
def get_place_detail(place_id: str, db: Session = Depends(get_db)):
    """특정 장소 상세 조회"""
    return db.query(models.KtoPetPlace).filter(
        models.KtoPetPlace.place_id == place_id
    ).first()


@router.get("/recommend/by-pet-weight")
def recommend_by_weight(
    pet_weight: float = Query(..., description="반려견 몸무게(kg)"),
    min_rating: float = Query(4.0),
    db: Session = Depends(get_db)
):
    """
    반려견 몸무게 기반 맞춤 장소 추천 (시나리오 3, 4)
    pet_policy에 대형견/소형견 텍스트 포함 여부로 필터링
    """
    from sqlalchemy import text
    sql = text("""
        SELECT DISTINCT p.place_id, p.place_name, p.category,
                        p.latitude, p.longitude, p.pet_policy
        FROM place_reviews r
        JOIN kto_pet_places p  ON r.place_id = p.place_id
        JOIN user_pet_map   m  ON r.user_id  = m.user_id
        JOIN pets          pt  ON m.pet_id   = pt.pet_id
        WHERE pt.pet_weight >= :weight
          AND r.rating       >= :min_rating
    """)
    rows = db.execute(sql, {"weight": pet_weight, "min_rating": min_rating}).fetchall()
    return [dict(r._mapping) for r in rows]
