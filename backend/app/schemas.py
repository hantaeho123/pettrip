from pydantic import BaseModel
from typing import Optional, List

# ── Place ──────────────────────────────────────────────
class PlaceBase(BaseModel):
    place_id:   str
    place_name: str
    category:   Optional[str] = None
    latitude:   Optional[float] = None
    longitude:  Optional[float] = None
    pet_policy: Optional[str] = None

class PlaceOut(PlaceBase):
    class Config:
        from_attributes = True

# ── Review ─────────────────────────────────────────────
class ReviewCreate(BaseModel):
    place_id: str
    user_id:  int
    rating:   int
    comment:  Optional[str] = None

class ReviewOut(ReviewCreate):
    review_id: int
    nickname:  Optional[str] = None

    class Config:
        from_attributes = True

# ── Pet ────────────────────────────────────────────────
class PetCreate(BaseModel):
    pet_name:   str
    pet_breed:  Optional[str] = None
    pet_weight: Optional[float] = None

class PetOut(PetCreate):
    pet_id: int

    class Config:
        from_attributes = True

# ── User ───────────────────────────────────────────────
class UserCreate(BaseModel):
    nickname: str
    email:    str

class UserOut(UserCreate):
    user_id: int

    class Config:
        from_attributes = True
