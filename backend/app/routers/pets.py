"""
routers/pets.py
반려동물 프로필 / N:M 매핑 / 견종 랭킹 / 멍트립 다이어리

시나리오 2, 5와 연계.
- 펫 등록 및 공동 소유자 추가 (N:M)
- 견종별 인기 스팟 랭킹 (통계)
- 같은 펫을 공유하는 가족의 통합 방문 이력
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/user/{user_id}", response_model=List[schemas.PetOut])
def get_user_pets(user_id: int, db: Session = Depends(get_db)):
    """특정 유저가 소유한 (공동 소유 포함) 반려동물 목록."""
    rows = (
        db.query(models.Pet)
        .join(models.UserPetMap, models.Pet.pet_id == models.UserPetMap.pet_id)
        .filter(models.UserPetMap.user_id == user_id)
        .all()
    )
    return rows


@router.post("/", response_model=schemas.PetOut)
def create_pet(pet: schemas.PetCreate, user_id: int, db: Session = Depends(get_db)):
    """반려동물 등록 + 등록한 유저를 소유자로 매핑."""
    new_pet = models.Pet(**pet.model_dump())
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    mapping = models.UserPetMap(user_id=user_id, pet_id=new_pet.pet_id)
    db.add(mapping)
    db.commit()
    return new_pet


@router.post("/{pet_id}/co-owner/{user_id}")
def add_co_owner(pet_id: int, user_id: int, db: Session = Depends(get_db)):
    """[시나리오 2] 반려동물에 공동 소유자 추가 (N:M 관계)."""
    exists = db.query(models.UserPetMap).filter(
        models.UserPetMap.pet_id == pet_id,
        models.UserPetMap.user_id == user_id,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="이미 공동 소유자로 등록되어 있습니다.")

    db.add(models.UserPetMap(user_id=user_id, pet_id=pet_id))
    db.commit()
    return {"message": "공동 소유자로 등록되었습니다."}


@router.get("/ranking/{breed}", response_model=List[schemas.RankingItem])
def breed_ranking(breed: str, db: Session = Depends(get_db)):
    """
    [시나리오 5] 견종별 인기 스팟 랭킹.
    해당 견종 견주들이 4점 이상 준 장소를 평균 평점순으로 집계.
    """
    rows = db.execute(text("""
        SELECT p.place_id, p.place_name, p.category,
               ROUND(AVG(r.rating), 1) AS avg_rating,
               COUNT(r.review_id)       AS review_count
        FROM place_reviews r
        JOIN kto_pet_places p ON r.place_id = p.place_id
        JOIN user_pet_map   m ON r.user_id  = m.user_id
        JOIN pets          pt ON m.pet_id   = pt.pet_id
        WHERE pt.pet_breed = :breed
          AND r.rating    >= 4
        GROUP BY p.place_id, p.place_name, p.category
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT 10
    """), {"breed": breed}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/diary/{pet_id}", response_model=List[schemas.DiaryEntry])
def pet_diary(pet_id: int, db: Session = Depends(get_db)):
    """
    [시나리오 2] 멍트립 다이어리.
    같은 펫을 공동 소유한 모든 유저의 방문 리뷰를 통합해서 보여준다.
    (아빠가 남긴 리뷰가 엄마 화면에도 '초코가 다녀온 곳'으로 표시)
    """
    rows = db.execute(text("""
        SELECT DISTINCT
            pt.pet_name,
            p.place_name,
            r.rating,
            u.nickname,
            r.comment
        FROM pets pt
        JOIN user_pet_map  m ON pt.pet_id  = m.pet_id
        JOIN app_users     u ON m.user_id  = u.user_id
        JOIN place_reviews r ON u.user_id  = r.user_id
        JOIN kto_pet_places p ON r.place_id = p.place_id
        WHERE pt.pet_id = :pid
        ORDER BY r.rating DESC
    """), {"pid": pet_id}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/breeds/list")
def list_breeds(db: Session = Depends(get_db)):
    """랭킹 드롭다운용: 등록된 견종 목록 (리뷰가 있는 것 우선)."""
    rows = db.execute(text("""
        SELECT DISTINCT pet_breed
        FROM pets
        WHERE pet_breed IS NOT NULL
        ORDER BY pet_breed
    """)).fetchall()
    return [r[0] for r in rows]
