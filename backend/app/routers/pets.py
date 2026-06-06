from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[schemas.PetOut])
def get_pets_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    특정 유저의 반려동물 목록 조회
    user_pet_map(N:M) 테이블 통해 공동 소유 반려동물도 포함 (시나리오 5)
    """
    rows = (
        db.query(models.Pet)
        .join(models.UserPetMap, models.Pet.pet_id == models.UserPetMap.pet_id)
        .filter(models.UserPetMap.user_id == user_id)
        .all()
    )
    return rows


@router.post("/", response_model=schemas.PetOut)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    """반려동물 등록"""
    new_pet = models.Pet(**pet.model_dump())
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return new_pet


@router.post("/{pet_id}/owner/{user_id}")
def add_pet_owner(pet_id: int, user_id: int, db: Session = Depends(get_db)):
    """반려동물 공동 소유자 추가 (N:M 관계)"""
    mapping = models.UserPetMap(user_id=user_id, pet_id=pet_id)
    db.add(mapping)
    db.commit()
    return {"message": f"user {user_id} added as owner of pet {pet_id}"}


@router.get("/ranking/{breed}")
def get_ranking_by_breed(breed: str, db: Session = Depends(get_db)):
    """
    견종별 인기 스팟 랭킹 (시나리오 6)
    해당 견종 견주들이 4점 이상 준 장소를 평균 평점 순으로 반환
    """
    from sqlalchemy import text
    sql = text("""
        SELECT p.place_id, p.place_name, p.category,
               ROUND(AVG(r.rating)::numeric, 1) AS avg_rating,
               COUNT(r.review_id) AS review_count
        FROM place_reviews r
        JOIN kto_pet_places p  ON r.place_id = p.place_id
        JOIN user_pet_map   m  ON r.user_id  = m.user_id
        JOIN pets          pt  ON m.pet_id   = pt.pet_id
        WHERE pt.pet_breed = :breed
          AND r.rating     >= 4
        GROUP BY p.place_id, p.place_name, p.category
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT 10
    """)
    rows = db.execute(sql, {"breed": breed}).fetchall()
    return [dict(r._mapping) for r in rows]
