"""
database.py
PostgreSQL 연결 및 SQLAlchemy 세션 관리

- engine        : DB 연결 엔진 (DATABASE_URL 사용)
- SessionLocal  : 요청마다 생성되는 DB 세션 팩토리
- get_db()      : FastAPI 의존성 주입용 세션 생성기
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# .env의 DATABASE_URL 사용. 없으면 로컬 기본값.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/pettrip"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 라우터에서 Depends(get_db)로 주입받는 DB 세션."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
