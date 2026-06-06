from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/{place_id}", response_model=List[schemas.ReviewOut])
def get_reviews(place_id: str, db: Session = Depends(get_db)):
    """특정 장소의 리뷰 목록 + 작성자 닉네임 조회 (시나리오 2)"""
    rows = (
        db.query(models.PlaceReview, models.AppUser.nickname)
        .join(models.AppUser, models.PlaceReview.user_id == models.AppUser.user_id)
        .filter(models.PlaceReview.place_id == place_id)
        .order_by(models.PlaceReview.review_id.desc())
        .all()
    )
    result = []
    for review, nickname in rows:
        item = schemas.ReviewOut.model_validate(review)
        item.nickname = nickname
        result.append(item)
    return result


@router.post("/", response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """리뷰 등록"""
    new_review = models.PlaceReview(**review.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
