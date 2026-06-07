"""
models.py
SQLAlchemy ORM 모델 정의 (sql/ddl.sql 스키마와 1:1 대응)

테이블 5개 + 관계:
  kto_pet_places  (실제 데이터 - 관광공사 API)
  app_users       (가상 데이터 - 사용자)
  pets            (가상 데이터 - 반려동물)
  user_pet_map    (N:M 관계 매핑)
  place_reviews   (가상 데이터 - 리뷰)
"""

from sqlalchemy import (
    Column, String, Integer, Numeric, Text, Boolean,
    ForeignKey, CheckConstraint, TIMESTAMP, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class KtoPetPlace(Base):
    """한국관광공사 반려동물 동반여행 API 장소 정보 (실제 데이터)"""
    __tablename__ = "kto_pet_places"

    place_id          = Column(String(50), primary_key=True)
    place_name        = Column(String(100), nullable=False)
    category          = Column(String(50))
    address           = Column(String(255))
    latitude          = Column(Numeric(10, 7))
    longitude         = Column(Numeric(10, 7))

    # 반려동물 정책
    pet_size_limit    = Column(String(100))
    max_weight_limit  = Column(Numeric(5, 2))
    pet_policy        = Column(Text)
    pet_type_code     = Column(String(50))

    # 화면 표시용 추가 정보
    amenities         = Column(Text)
    purchase_items    = Column(Text)
    rental_items      = Column(Text)
    safety_hazards    = Column(Text)
    extra_info        = Column(Text)
    pet_fee_info      = Column(String(255))
    main_image_url    = Column(Text)

    # 운영 정보
    operating_hours   = Column(String(255))
    closed_days       = Column(String(255))
    parking_info      = Column(String(255))
    contact_number    = Column(String(50))
    website_url       = Column(Text)

    # 가공 boolean
    is_indoor_allowed = Column(Boolean, default=False)
    has_outdoor_yard  = Column(Boolean, default=False)

    updated_at        = Column(TIMESTAMP, server_default=func.now())

    reviews = relationship("PlaceReview", back_populates="place", cascade="all, delete")


class AppUser(Base):
    """서비스 사용자 (가상 데이터). 비밀번호는 bcrypt 해시로 저장."""
    __tablename__ = "app_users"

    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    nickname      = Column(String(50), nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at    = Column(TIMESTAMP, server_default=func.now())

    pet_mappings = relationship("UserPetMap", back_populates="user", cascade="all, delete")
    reviews      = relationship("PlaceReview", back_populates="user", cascade="all, delete")


class Pet(Base):
    """반려동물 개체 (가상 데이터)"""
    __tablename__ = "pets"

    pet_id     = Column(Integer, primary_key=True, autoincrement=True)
    pet_name   = Column(String(50), nullable=False)
    pet_breed  = Column(String(50))
    pet_weight = Column(Numeric(5, 2))

    user_mappings = relationship("UserPetMap", back_populates="pet", cascade="all, delete")


class UserPetMap(Base):
    """주인↔반려동물 N:M 매핑 (복합 PK로 중복 방지)"""
    __tablename__ = "user_pet_map"

    user_id = Column(Integer, ForeignKey("app_users.user_id", ondelete="CASCADE"), primary_key=True)
    pet_id  = Column(Integer, ForeignKey("pets.pet_id",       ondelete="CASCADE"), primary_key=True)

    user = relationship("AppUser", back_populates="pet_mappings")
    pet  = relationship("Pet",     back_populates="user_mappings")


class PlaceReview(Base):
    """장소 방문 후기 및 평점 (가상 데이터). 사진 공유 지원."""
    __tablename__ = "place_reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5"),)

    review_id  = Column(Integer, primary_key=True, autoincrement=True)
    place_id   = Column(String(50), ForeignKey("kto_pet_places.place_id", ondelete="CASCADE"))
    user_id    = Column(Integer,    ForeignKey("app_users.user_id",        ondelete="CASCADE"))
    rating     = Column(Integer)
    comment    = Column(Text)
    photo_url  = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    place = relationship("KtoPetPlace", back_populates="reviews")
    user  = relationship("AppUser",     back_populates="reviews")
