"""
routers/reviews.py
리뷰 조회 / 작성 / 삭제 + 사진 업로드 엔드포인트

- 리뷰 작성 시 반려동물 사진을 함께 업로드 가능 (자랑하기 기능)
- 업로드된 이미지는 backend/uploads/ 에 저장되고 URL 경로를 DB에 기록
- 자랑게시판은 사진이 있는 리뷰를 최신순으로 모아서 보여줌
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import os
import uuid
import shutil
from app.database import get_db
from app import models, schemas

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/place/{place_id}", response_model=List[schemas.ReviewOut])
def get_place_reviews(place_id: str, db: Session = Depends(get_db)):
    """특정 장소의 리뷰 목록 + 작성자 닉네임 (최신순)."""
    rows = db.execute(text("""
        SELECT r.review_id, r.place_id, r.user_id, r.rating,
               r.comment, r.photo_url, r.created_at, u.nickname
        FROM place_reviews r
        JOIN app_users u ON r.user_id = u.user_id
        WHERE r.place_id = :pid
        ORDER BY r.created_at DESC
    """), {"pid": place_id}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post("/", response_model=schemas.ReviewOut)
def create_review(
    place_id: str = Form(...),
    user_id:  int = Form(...),
    rating:   int = Form(...),
    comment:  Optional[str] = Form(None),
    photo:    Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    리뷰 작성. 사진 파일이 첨부되면 서버에 저장하고 경로를 기록한다.
    multipart/form-data로 받기 때문에 Form/File을 사용.
    """
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="평점은 1~5 사이여야 합니다.")

    photo_url = None
    if photo and photo.filename:
        # 고유 파일명 생성 (확장자 유지)
        ext = os.path.splitext(photo.filename)[1]
        fname = f"{uuid.uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_url = f"/uploads/{fname}"

    review = models.PlaceReview(
        place_id  = place_id,
        user_id   = user_id,
        rating    = rating,
        comment   = comment,
        photo_url = photo_url,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # 닉네임 포함하여 반환
    user = db.query(models.AppUser).filter(models.AppUser.user_id == user_id).first()
    out = schemas.ReviewOut.model_validate(review)
    out.nickname = user.nickname if user else None
    return out


@router.delete("/{review_id}")
def delete_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    """리뷰 삭제 (본인이 작성한 리뷰만)."""
    review = db.query(models.PlaceReview).filter(
        models.PlaceReview.review_id == review_id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인이 작성한 리뷰만 삭제할 수 있습니다.")

    db.delete(review)
    db.commit()
    return {"message": "리뷰가 삭제되었습니다."}


@router.get("/feed", response_model=List[schemas.ReviewOut])
def get_community_feed(limit: int = 30, db: Session = Depends(get_db)):
    """
    자랑게시판 피드: 사진이 첨부된 리뷰를 최신순으로.
    장소명도 함께 보여주기 위해 JOIN.
    """
    rows = db.execute(text("""
        SELECT r.review_id, r.place_id, r.user_id, r.rating,
               r.comment, r.photo_url, r.created_at,
               u.nickname, p.place_name
        FROM place_reviews r
        JOIN app_users u      ON r.user_id  = u.user_id
        JOIN kto_pet_places p ON r.place_id = p.place_id
        WHERE r.photo_url IS NOT NULL
        ORDER BY r.created_at DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    result = []
    for r in rows:
        d = dict(r._mapping)
        # place_name을 comment 앞에 표시하기 위해 별도 필드로 넘기기보다
        # ReviewOut에 맞춰 반환 (place_name은 프론트에서 별도 조회 가능)
        result.append(d)
    return result
