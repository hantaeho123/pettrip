"""
routers/stats.py
통계/분석 엔드포인트 (ROLLUP OLAP 시연)

시설 카테고리 × 야외마당 유무별 평점을 소계/총계와 함께 집계.
보고서의 가산점 요소(ROLLUP) 시연용.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()


@router.get("/rollup")
def category_rollup(db: Session = Depends(get_db)):
    """
    [ROLLUP] 카테고리 × 야외마당 유무별 평균 평점과 리뷰 수.
    GROUP BY ROLLUP으로 분류 소계와 전체 총계가 함께 나온다.
    """
    rows = db.execute(text("""
        SELECT
            COALESCE(p.category, '전체 총계')                          AS category,
            COALESCE(CAST(p.has_outdoor_yard AS VARCHAR), '분류 소계')  AS outdoor,
            ROUND(AVG(r.rating), 2)                                   AS avg_rating,
            COUNT(r.review_id)                                        AS total_reviews
        FROM kto_pet_places p
        JOIN place_reviews  r ON p.place_id = r.place_id
        GROUP BY ROLLUP(p.category, p.has_outdoor_yard)
        ORDER BY p.category NULLS LAST, p.has_outdoor_yard NULLS LAST
    """)).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/summary")
def overall_summary(db: Session = Depends(get_db)):
    """전체 통계 요약 (대시보드용): 장소/유저/펫/리뷰 수."""
    res = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM kto_pet_places) AS total_places,
            (SELECT COUNT(*) FROM app_users)      AS total_users,
            (SELECT COUNT(*) FROM pets)           AS total_pets,
            (SELECT COUNT(*) FROM place_reviews)  AS total_reviews,
            (SELECT ROUND(AVG(rating), 2) FROM place_reviews) AS avg_rating
    """)).fetchone()
    return dict(res._mapping)
