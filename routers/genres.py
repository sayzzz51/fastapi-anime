from db import DB
from schemas import  Genre, GenrePost, timer
from dependencies import OrderOnly
from fastapi import HTTPException, APIRouter
from typing import List
from models import GenresORM
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("")
@timer
def get_genres(db: DB, order: OrderOnly) -> List[Genre]:
    genres = select(GenresORM)
    if order.order == "ASC":
        sorted_genres = genres.order_by(GenresORM.id.asc())
    else:
        sorted_genres = genres.order_by(GenresORM.id.desc())
    return db.scalars(sorted_genres).all()


@router.post("", status_code=201)
@timer
def post_genre(db: DB, data: GenrePost) -> Genre:
    new_genre = GenresORM(**data.model_dump())
    try:
        db.add(new_genre)
        db.commit()
        db.refresh(new_genre)
        return new_genre
    except IntegrityError:
        db.rollback()
        raise HTTPException(409)

