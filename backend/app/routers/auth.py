"""
routers/auth.py
회원가입 / 로그인 / 회원탈퇴 엔드포인트

- 비밀번호는 bcrypt로 해시하여 저장 (평문 저장 금지)
- 회원탈퇴 시 ON DELETE CASCADE로 리뷰·펫매핑이 자동 삭제됨
- 실제 서비스라면 JWT 토큰을 발급하겠지만, 과제 프로토타입이므로
  로그인 성공 시 user 정보를 반환하여 프론트가 보관하는 방식 사용
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.core.security import hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    """회원가입: 이메일 중복 확인 후 해시 비밀번호로 유저 생성."""
    exists = db.query(models.AppUser).filter(
        models.AppUser.email == payload.email
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    user = models.AppUser(
        nickname      = payload.nickname,
        email         = payload.email,
        password_hash = hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """로그인: 이메일로 유저 조회 후 비밀번호 해시 검증."""
    user = db.query(models.AppUser).filter(
        models.AppUser.email == payload.email
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    return {"user": user, "message": f"{user.nickname}님 환영합니다! 🐾"}


@router.delete("/users/{user_id}")
def delete_account(user_id: int, db: Session = Depends(get_db)):
    """회원탈퇴: CASCADE로 관련 리뷰·펫매핑 자동 삭제."""
    user = db.query(models.AppUser).filter(
        models.AppUser.user_id == user_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    db.delete(user)
    db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다. 관련 데이터가 모두 삭제되었습니다."}
