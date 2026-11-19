import os 
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postrgres://","postgresql+psycopg://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session

DB = Annotated[Session, Depends(get_db)]