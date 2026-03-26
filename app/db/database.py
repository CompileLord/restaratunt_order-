from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_URL



engine = create_engine(str(DB_URL), echo=True, connect_args={"check_same_thread": False})



SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

























