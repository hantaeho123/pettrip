from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class KtoPetPlace(Base):
    __tablename__ = "kto_pet_places"

    place_id   = Column(String(50), primary_key=True)
    place_name = Column(String(100), nullable=False)
    category   = Column(String(50))
    latitude   = Column(Float)
    longitude  = Column(Float)
    pet_policy = Column(Text)

    reviews = relationship("PlaceReview", back_populates="place", cascade="all, delete")


class AppUser(Base):
    __tablename__ = "app_users"

    user_id  = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(50), nullable=False)
    email    = Column(String(100), unique=True, nullable=False)

    pet_mappings = relationship("UserPetMap", back_populates="user", cascade="all, delete")
    reviews      = relationship("PlaceReview", back_populates="user", cascade="all, delete")


class Pet(Base):
    __tablename__ = "pets"

    pet_id     = Column(Integer, primary_key=True, autoincrement=True)
    pet_name   = Column(String(50), nullable=False)
    pet_breed  = Column(String(50))
    pet_weight = Column(Float)

    user_mappings = relationship("UserPetMap", back_populates="pet", cascade="all, delete")


class UserPetMap(Base):
    __tablename__ = "user_pet_map"

    user_id = Column(Integer, ForeignKey("app_users.user_id", ondelete="CASCADE"), primary_key=True)
    pet_id  = Column(Integer, ForeignKey("pets.pet_id",       ondelete="CASCADE"), primary_key=True)

    user = relationship("AppUser", back_populates="pet_mappings")
    pet  = relationship("Pet",     back_populates="user_mappings")


class PlaceReview(Base):
    __tablename__ = "place_reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5"),)

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    place_id  = Column(String(50), ForeignKey("kto_pet_places.place_id", ondelete="CASCADE"))
    user_id   = Column(Integer,    ForeignKey("app_users.user_id",        ondelete="CASCADE"))
    rating    = Column(Integer)
    comment   = Column(Text)

    place = relationship("KtoPetPlace", back_populates="reviews")
    user  = relationship("AppUser",     back_populates="reviews")
