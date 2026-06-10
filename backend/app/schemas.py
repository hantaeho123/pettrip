"""
schemas.py
Pydantic 스키마 - API 요청/응답의 데이터 형태를 정의하고 검증한다.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ── 장소 ───────────────────────────────────────────────────────────
class PlaceBase(BaseModel):
    place_id:   str
    place_name: str
    category:   Optional[str] = None
    address:    Optional[str] = None
    latitude:   Optional[Decimal] = None
    longitude:  Optional[Decimal] = None

class PlaceSummary(PlaceBase):
    """지도 마커/목록용 요약 정보"""
    pet_size_limit:    Optional[str] = None
    max_weight_limit:  Optional[Decimal] = None
    is_indoor_allowed: Optional[bool] = None
    has_outdoor_yard:  Optional[bool] = None
    main_image_url:    Optional[str] = None
    average_rating:    Optional[float] = None
    total_reviews:     Optional[int] = None

    class Config:
        from_attributes = True

class PlaceDetail(PlaceSummary):
    """상세 화면용 전체 정보"""
    pet_policy:      Optional[str] = None
    pet_type_code:   Optional[str] = None
    amenities:       Optional[str] = None
    purchase_items:  Optional[str] = None
    rental_items:    Optional[str] = None
    safety_hazards:  Optional[str] = None
    extra_info:      Optional[str] = None
    pet_fee_info:    Optional[str] = None
    operating_hours: Optional[str] = None
    closed_days:     Optional[str] = None
    parking_info:    Optional[str] = None
    contact_number:  Optional[str] = None
    website_url:     Optional[str] = None

    class Config:
        from_attributes = True


# ── 인증/유저 ──────────────────────────────────────────────────────
class UserRegister(BaseModel):
    nickname: str
    email:    EmailStr
    password: str

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class UserOut(BaseModel):
    user_id:  int
    nickname: str
    email:    str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user: UserOut
    message: str


# ── 반려동물 ───────────────────────────────────────────────────────
class PetCreate(BaseModel):
    pet_name:   str
    pet_breed:  Optional[str] = None
    pet_weight: Optional[float] = None

class PetOut(PetCreate):
    pet_id:      int
    invite_code: Optional[str] = None
    photo_url:   Optional[str] = None

    class Config:
        from_attributes = True


# ── 리뷰 ───────────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    place_id: str
    user_id:  int
    rating:   int
    comment:  Optional[str] = None
    photo_url: Optional[str] = None

class ReviewOut(BaseModel):
    review_id:  int
    place_id:   str
    user_id:    int
    rating:     int
    comment:    Optional[str] = None
    photo_url:  Optional[str] = None
    nickname:   Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── 랭킹 ───────────────────────────────────────────────────────────
class RankingItem(BaseModel):
    place_id:     str
    place_name:   str
    category:     Optional[str] = None
    avg_rating:   float
    review_count: int


# ── 멍트립 다이어리 ────────────────────────────────────────────────
class DiaryEntry(BaseModel):
    pet_name:   str
    place_name: str
    rating:     int
    nickname:   str
    comment:    Optional[str] = None
    created_at: Optional[datetime] = None
