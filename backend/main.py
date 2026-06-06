from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import places, reviews, pets, users
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PetTrip API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router, prefix="/api/places", tags=["places"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(pets.router, prefix="/api/pets", tags=["pets"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "PetTrip API is running 🐾"}
