"""
routers/pets.py
반려동물 프로필 / 공동 등록(초대코드) / 사진 업로드 / 견종 랭킹 / 멍트립 다이어리

- 펫 등록 시 6자리 초대코드 자동 생성
- 가족이 초대코드로 공동 소유자 등록 (N:M)
- 강아지 프로필 사진 업로드
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import os, uuid, shutil, random, string
from app.database import get_db
from app import models, schemas

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _generate_invite_code(db: Session) -> str:
    """중복 없는 6자리 초대코드 생성 (영문 대문자 + 숫자)."""
    for _ in range(100):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        exists = db.query(models.Pet).filter(models.Pet.invite_code == code).first()
        if not exists:
            return code
    raise HTTPException(status_code=500, detail="초대코드 생성 실패. 다시 시도해주세요.")


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
def create_pet(
    pet_name:   str = Form(...),
    pet_breed:  Optional[str] = Form(None),
    pet_weight: Optional[float] = Form(None),
    user_id:    int = Form(...),
    photo:      Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    반려동물 등록.
    - 자동으로 6자리 초대코드 생성
    - 프로필 사진 첨부 가능
    - 등록한 유저를 소유자로 매핑
    """
    # 사진 저장
    photo_url = None
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1]
        fname = f"pet_{uuid.uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as buf:
            shutil.copyfileobj(photo.file, buf)
        photo_url = f"/uploads/{fname}"

    invite_code = _generate_invite_code(db)

    new_pet = models.Pet(
        pet_name=pet_name,
        pet_breed=pet_breed,
        pet_weight=pet_weight,
        invite_code=invite_code,
        photo_url=photo_url,
    )
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    # 등록자를 소유자로 매핑
    db.add(models.UserPetMap(user_id=user_id, pet_id=new_pet.pet_id))
    db.commit()
    return new_pet


@router.put("/{pet_id}/photo", response_model=schemas.PetOut)
def update_pet_photo(
    pet_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """강아지 프로필 사진 변경."""
    pet = db.query(models.Pet).filter(models.Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="반려동물을 찾을 수 없습니다.")

    ext = os.path.splitext(photo.filename)[1]
    fname = f"pet_{uuid.uuid4().hex}{ext}"
    fpath = os.path.join(UPLOAD_DIR, fname)
    with open(fpath, "wb") as buf:
        shutil.copyfileobj(photo.file, buf)

    pet.photo_url = f"/uploads/{fname}"
    db.commit()
    db.refresh(pet)
    return pet


@router.post("/join-by-code")
def join_by_invite_code(
    invite_code: str,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    초대코드로 공동 소유자 등록.
    가족이 같은 강아지의 초대코드를 입력하면 공동 소유 관계가 생긴다.
    """
    pet = db.query(models.Pet).filter(models.Pet.invite_code == invite_code).first()
    if not pet:
        raise HTTPException(status_code=404, detail="유효하지 않은 초대코드입니다.")

    exists = db.query(models.UserPetMap).filter(
        models.UserPetMap.pet_id == pet.pet_id,
        models.UserPetMap.user_id == user_id,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="이미 등록된 반려동물이에요.")

    db.add(models.UserPetMap(user_id=user_id, pet_id=pet.pet_id))
    db.commit()
    return {"message": f"{pet.pet_name}의 공동 소유자로 등록되었습니다! 🐾", "pet_name": pet.pet_name}


@router.post("/{pet_id}/co-owner/{user_id}")
def add_co_owner(pet_id: int, user_id: int, db: Session = Depends(get_db)):
    """반려동물에 공동 소유자 추가 (직접 pet_id 지정 방식)."""
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
    """견종별 인기 스팟 랭킹."""
    rows = db.execute(text("""
        SELECT p.place_id, p.place_name, p.category,
               ROUND(AVG(r.rating), 1) AS avg_rating,
               COUNT(r.review_id)       AS review_count
        FROM place_reviews r
        JOIN kto_pet_places p ON r.place_id = p.place_id
        JOIN user_pet_map   m ON r.user_id  = m.user_id
        JOIN pets          pt ON m.pet_id   = pt.pet_id
        WHERE pt.pet_breed = :breed AND r.rating >= 4
        GROUP BY p.place_id, p.place_name, p.category
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT 10
    """), {"breed": breed}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/diary/{pet_id}", response_model=List[schemas.DiaryEntry])
def pet_diary(pet_id: int, db: Session = Depends(get_db)):
    """멍트립 다이어리: 공동 소유 가족 전원의 통합 방문 이력."""
    rows = db.execute(text("""
        SELECT DISTINCT
            pt.pet_name, p.place_name, r.rating, u.nickname, r.comment
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
    """등록된 견종 목록."""
    rows = db.execute(text("""
        SELECT DISTINCT pet_breed FROM pets
        WHERE pet_breed IS NOT NULL ORDER BY pet_breed
    """)).fetchall()
    return [r[0] for r in rows]
