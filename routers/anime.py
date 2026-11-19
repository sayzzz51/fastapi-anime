from db import DB
from schemas import AnimeEdit, Anime, AnimePost, Review, ReviewPost, Status, AnimeRating
from schemas import timer, AnimeWgenres, anime_with_genres, AnimeTop
from dependencies import ErrorCheckAnime, ErrorCheckGenre, Pagination, Sorting, OrderOnly
from fastapi import Query, HTTPException, APIRouter
from typing import List, Annotated
from models import AnimeORM, AnimeGenreORM, GenresORM, ReviewORM
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("")
@timer
def get_anime(db: DB, page: Pagination, sort_by: Sorting, status: Status | None = None, 
min_year: Annotated[int, Query(ge=1960, le=2030)] | None = None, 
genre: Annotated[str, Query(max_length=50)] | None = None) -> List[Anime]:
    query = select(AnimeORM)
    if status is not None:
        query = query.where(AnimeORM.status == status)
    if min_year is not None:
        query = query.where(AnimeORM.year >= min_year)
    if genre is not None:
        query = (
            query.join(AnimeGenreORM, AnimeGenreORM.anime_id == AnimeORM.id)
            .join(GenresORM, GenresORM.id == AnimeGenreORM.genre_id)
            .where(GenresORM.name.ilike(genre))
            .distinct()
            )
    column = getattr(AnimeORM, sort_by.sort)

    if sort_by.order == "DESC":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())
    query = query.order_by(AnimeORM.id).limit(page.limit).offset(page.offset)
    return db.scalars(query).all()
    

@router.get("/top")
@timer
def get_top(db: DB) -> List[AnimeTop]:
    top = (select(AnimeORM.id, AnimeORM.title, AnimeORM.year, AnimeORM.episodes, AnimeORM.status,
                    func.count(ReviewORM.id).label("review_count"), 
                    func.round(func.avg(ReviewORM.score), 2).label("average_score"))
                    .join(ReviewORM, ReviewORM.anime_id == AnimeORM.id)
                    .group_by(AnimeORM.id)
                    .having(func.count(ReviewORM.id) >= 3 )
                    .order_by(func.round(func.avg(ReviewORM.score), 2).desc())
                    .limit(5))
    topped = db.execute(top).all()
    return topped


@router.get("/{anime_id}/rating")
@timer
def get_rating_anime(db: DB, anime_id: int, _: ErrorCheckAnime) -> AnimeRating:
    rated = (select(func.count(ReviewORM.id).label("review_count"), 
                    func.round(func.avg(ReviewORM.score), 2).label("average_score"))
                    .where(ReviewORM.anime_id == anime_id))
    resp = db.execute(rated).one()
    return {"anime_id": anime_id, **resp._asdict()}
    


@router.post("", status_code=201)
@timer
def post_anime(db: DB, data: AnimePost) -> Anime:
    new_anime = AnimeORM(**data.model_dump())
    try:
        db.add(new_anime)
        db.commit()
        db.refresh(new_anime)
        return new_anime
    except IntegrityError:
        db.rollback()
        raise HTTPException(409)


@router.patch("/{anime_id}")
@timer
def edit_anime(db: DB, anime: ErrorCheckAnime, data: AnimeEdit) -> Anime:
    updated = data.model_dump(exclude_unset=True, exclude_none=True)
    if not updated:
        raise HTTPException(400)
    try:
        for key, value in updated.items():
            setattr(anime, key, value)
        db.commit()
        db.refresh(anime)
        return anime
    except IntegrityError:
        db.rollback()
        raise HTTPException(409)


@router.delete("/{anime_id}", status_code=204)
@timer
def delete_anime(db: DB, anime: ErrorCheckAnime, anime_id: int) -> None:
    db.delete(anime)
    db.commit()
    return


@router.get("/{anime_id}")
@timer
def get_anime(db: DB, anime: ErrorCheckAnime, anime_id: int) -> AnimeWgenres:
    ani_dict = Anime.model_validate(anime).model_dump() 
    return {**ani_dict, "genres": anime_with_genres(db, anime_id)}


@router.post("/{anime_id}/genres/{genre_id}", status_code=201)
@timer
def conn_tables(db: DB, anime_id: int, genre_id: int,
genre: ErrorCheckGenre, anime: ErrorCheckAnime) -> AnimeWgenres:
    link = AnimeGenreORM(anime_id=anime.id, genre_id=genre.id)
    try:
        db.add(link)
        db.commit()
        db.refresh(link)
        ani_dict = Anime.model_validate(anime).model_dump() 
        return {**ani_dict, "genres": anime_with_genres(db, anime_id)}
    except IntegrityError:
        db.rollback()
        raise HTTPException(409)
    


@router.delete("/{anime_id}/genres/{genre_id}", status_code=204)
@timer
def disconn_tables(db: DB, genre: ErrorCheckGenre, anime: ErrorCheckAnime) -> None:
    link = db.get(AnimeGenreORM, (anime.id, genre.id))
    if link is None:
        raise HTTPException(404)
    db.delete(link)
    db.commit()


@router.get("/{anime_id}/reviews")
@timer
def get_reviews(db: DB, page: Pagination, order: OrderOnly, _: ErrorCheckAnime, anime_id: int) -> List[Review]:
    query = select(ReviewORM)
    query = query.where(ReviewORM.anime_id == anime_id)
    if order.order == "ASC":
        query = query.order_by(ReviewORM.id.asc())
    else:
        query = query.order_by(ReviewORM.id.desc())
    query = query.offset(page.offset).limit(page.limit)
    return db.scalars(query).all()


@router.post("/{anime_id}/reviews", status_code=201)
@timer
def post_reviews(db: DB, data: ReviewPost, _: ErrorCheckAnime) -> Review:
    new_review = ReviewORM(**data.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review












    







        


     
    