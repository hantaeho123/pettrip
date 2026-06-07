"""
routers/places.py
장소 탐색 / 상세 조회 / 개인화 필터링 엔드포인트

시나리오 1, 3, 4와 연계되는 핵심 라우터.
- 지도 좌표 범위(bounding box) + 카테고리 필터 조회
- VIEW(vw_place_detail_stats)로 평균 평점·리뷰 수 즉시 로딩
- 반려견 몸무게 기반 개인화 추천
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.PlaceSummary])
def list_places(
    category: Optional[str]  = Query(None, description="카테고리 (카페/식당/숙소/공원/관광지)"),
    min_lat:  Optional[float] = Query(None, description="지도 범위 최소 위도"),
    max_lat:  Optional[float] = Query(None, description="지도 범위 최대 위도"),
    min_lng:  Optional[float] = Query(None, description="지도 범위 최소 경도"),
    max_lng:  Optional[float] = Query(None, description="지도 범위 최대 경도"),
    keyword:  Optional[str]  = Query(None, description="장소명/주소 검색어"),
    max_weight: Optional[float] = Query(None, description="반려견 몸무게(kg) - 이 무게 이상 허용하는 곳만"),
    indoor_only: bool = Query(False, description="실내 동반 가능한 곳만"),
    limit:    int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    """
    지도/목록용 장소 조회.
    VIEW를 활용해 평균 평점·리뷰 수까지 한 번에 가져온다.
    여러 필터(좌표·카테고리·검색어·몸무게·실내)를 동적으로 조합.
    """
    # VIEW + 원본 테이블 JOIN으로 통계와 상세 정보를 함께 조회
    conditions = []
    params = {"limit": limit}

    if category:
        conditions.append("v.category = :category")
        params["category"] = category
    if min_lat is not None and max_lat is not None:
        conditions.append("v.latitude BETWEEN :min_lat AND :max_lat")
        params["min_lat"] = min_lat
        params["max_lat"] = max_lat
    if min_lng is not None and max_lng is not None:
        conditions.append("v.longitude BETWEEN :min_lng AND :max_lng")
        params["min_lng"] = min_lng
        params["max_lng"] = max_lng
    if keyword:
        conditions.append("(v.place_name ILIKE :kw OR v.address ILIKE :kw)")
        params["kw"] = f"%{keyword}%"
    if max_weight is not None:
        # 반려견 몸무게 이상을 허용하는 장소만 (max_weight_limit이 NULL이면 제한 없음으로 간주)
        conditions.append("(v.max_weight_limit IS NULL OR v.max_weight_limit >= :mw)")
        params["mw"] = max_weight
    if indoor_only:
        conditions.append("v.is_indoor_allowed = TRUE")

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    sql = text(f"""
        SELECT v.place_id, v.place_name, v.category, v.address,
               v.latitude, v.longitude, v.max_weight_limit,
               v.is_indoor_allowed, v.has_outdoor_yard, v.main_image_url,
               p.pet_size_limit,
               v.average_rating, v.total_reviews
        FROM vw_place_detail_stats v
        JOIN kto_pet_places p ON v.place_id = p.place_id
        {where_clause}
        ORDER BY v.total_reviews DESC
        LIMIT :limit
    """)

    rows = db.execute(sql, params).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{place_id}", response_model=schemas.PlaceDetail)
def get_place_detail(place_id: str, db: Session = Depends(get_db)):
    """
    장소 상세 조회.
    원본 테이블의 전체 컬럼 + VIEW의 평점 통계를 합쳐서 반환.
    """
    place = db.query(models.KtoPetPlace).filter(
        models.KtoPetPlace.place_id == place_id
    ).first()
    if not place:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")

    # VIEW에서 평점 통계 가져오기
    stats = db.execute(text("""
        SELECT average_rating, total_reviews
        FROM vw_place_detail_stats WHERE place_id = :pid
    """), {"pid": place_id}).fetchone()

    result = schemas.PlaceDetail.model_validate(place)
    if stats:
        result.average_rating = float(stats.average_rating)
        result.total_reviews  = stats.total_reviews
    return result


@router.get("/recommend/for-pet/{pet_id}", response_model=List[schemas.PlaceSummary])
def recommend_for_pet(
    pet_id: int,
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    [시나리오 4] 등록된 반려견 프로필 기준 맞춤 추천.
    펫 몸무게를 읽어와서, 그 무게를 수용하는 평점 높은 장소만 반환.
    """
    pet = db.query(models.Pet).filter(models.Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="반려동물을 찾을 수 없습니다.")

    weight = float(pet.pet_weight or 0)

    conditions = ["(v.max_weight_limit IS NULL OR v.max_weight_limit >= :w)",
                  "v.average_rating >= 4.0"]
    params = {"w": weight}
    if category:
        conditions.append("v.category = :category")
        params["category"] = category

    sql = text(f"""
        SELECT v.place_id, v.place_name, v.category, v.address,
               v.latitude, v.longitude, v.max_weight_limit,
               v.is_indoor_allowed, v.has_outdoor_yard, v.main_image_url,
               v.average_rating, v.total_reviews
        FROM vw_place_detail_stats v
        WHERE {' AND '.join(conditions)}
        ORDER BY v.average_rating DESC, v.total_reviews DESC
        LIMIT 100
    """)
    rows = db.execute(sql, params).fetchall()
    return [dict(r._mapping) for r in rows]
