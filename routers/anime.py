from db import DB
from schemas import AnimeBase, AnimeEdit, Anime, AnimePost, ReviewBase, Review, ReviewPost, Status, AnimeRating
from schemas import GenreBase, Genre, GenrePost, timer, AnimeWgenres, anime_with_genres, ReviewWanime, AnimeTop
from dependencies import ErrorCheckAnime, ErrorCheckGenre, Pagination, Sorted
from fastapi import FastAPI, Query, Path, HTTPException, Depends, Body, APIRouter
from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

router = APIRouter(prefix="/anime", tags=["anime"])

### get


@router.get("")
@timer
def get_anime(db: DB, page: Pagination, sort: Sorted, status: Status | None = None, min_year: Annotated[int, Query(ge=1960, le=2030)] | None = None, 
genre: Annotated[str, Query(max_length=50)] | None = None) -> List[Anime]:
    query = "SELECT DISTINCT anime.* FROM anime "
    conditions = [] 
    params = []
    if genre is not None:
        query += "LEFT JOIN anime_genre ON anime_genre.anime_id = anime.id LEFT JOIN genres ON genres.id = anime_genre.genre_id"
        conditions.append("genres.name ILIKE %s")
        params.append(genre)  
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    if min_year is not None:
            conditions.append("year >= %s")
            params.append(min_year)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += sort
    query += " LIMIT %s OFFSET %s"
    params.append(page.limit)
    params.append(page.offset)
    result = db.execute(query, params).fetchall()
    return result



@router.get("/top")
@timer
def get_top(db: DB) -> List[AnimeTop]:
    request = db.execute('''SELECT anime.id, anime.title, anime.year, anime.episodes, anime.status, 
    COUNT(reviews.id) AS review_count, 
    ROUND(AVG(reviews.score),2) AS average_score FROM anime 
    LEFT JOIN reviews ON reviews.anime_id = anime.id 
    GROUP BY anime.id HAVING COUNT(reviews.id) >=3
    ORDER BY average_score DESC, review_count DESC LIMIT 5 ''')
    response = request.fetchall()
    return response
    

@router.get("/{anime_id}")
@timer
def get_anime_id(db: DB, anime_id: Annotated[int, Path(ge=1)], anime: ErrorCheckAnime) -> AnimeWgenres:
    return {**anime, "genres": anime_with_genres(db, anime_id)}


@router.get("/{anime_id}/reviews")
@timer
def get_reviews(db: DB, anime_id: Annotated[int, Path(ge=1)], page: Pagination, _: ErrorCheckAnime) -> List:
    return db.execute("SELECT reviews.id, reviews.author, reviews.score, reviews.text FROM reviews WHERE anime_id = %s LIMIT %s OFFSET %s",
    (anime_id, page.limit, page.offset)).fetchall()


@router.get("/{anime_id}/rating")
@timer
def get_avg(db: DB, _: ErrorCheckAnime, anime_id: Annotated[int, Path(ge=1)]) -> AnimeRating:
    averaged = db.execute("SELECT COUNT(reviews.id) AS review_count, ROUND(AVG(reviews.score),2) AS average_score FROM reviews WHERE anime_id = %s",
    (anime_id,)).fetchone()
    return {"anime_id": anime_id, **averaged}


### post


@router.post("/{anime_id}/genres/{genre_id}", status_code=201)
@timer
def conn_genre(db: DB, anime: ErrorCheckAnime, genre: ErrorCheckGenre, 
    anime_id: Annotated[int, Path(ge=1)], genre_id: Annotated[int, Path(ge=1)]) -> AnimeWgenres:
    try:
        db.execute("INSERT into anime_genre (anime_id, genre_id) VALUES (%s, %s) RETURNING *",(anime_id, genre_id))
        db.commit()
        return {**anime, "genres": anime_with_genres(db, anime_id)}
    except psycopg.errors.UniqueViolation:
        db.rollback()
        raise HTTPException(409)


@router.post("", status_code=201)
@timer
def post_anime(db: DB, data: AnimePost) -> Anime:
    try:
        posted = db.execute("INSERT INTO anime (title, year, episodes, status) VALUES (%s, %s, %s, %s) RETURNING *", 
        (data.title, data.year, data.episodes, data.status)).fetchone()
        db.commit()
        return posted
    except psycopg.errors.UniqueViolation:
        db.rollback()
        raise HTTPException(409)


@router.post("/{anime_id}/reviews", status_code=201)
def post_review(db: DB, data: ReviewPost, anime_id: Annotated[int, Path(ge=1)], _: ErrorCheckAnime) -> Review:
    response = db.execute("INSERT INTO reviews (anime_id, author, score, text) VALUES (%s, %s, %s, %s) RETURNING *",
    (anime_id, data.author, data.score, data.text)).fetchone()
    return response


### patch


@router.patch("/{anime_id}")
def edit_anime(db: DB, anime_id: Annotated[int, Path(ge=1)], anime_or404: ErrorCheckAnime, data: AnimeEdit) -> Anime:
    try:
        conditions = []
        params = []
        updated = data.model_dump(exclude_unset=True, exclude_none=True)
        if not updated:
            raise HTTPException(400, "Измените хотя бы один параметр")
        for key, value in updated.items():
            conditions.append(f"{key} = " + "%s")
            params.append(value)
        params.append(anime_id)
        query = "UPDATE anime SET " + ", ".join(conditions) + " WHERE id = %s RETURNING *"
        result = db.execute(query, params).fetchone()
        db.commit()
        return result
    except psycopg.errors.UniqueViolation:
        db.rollback()
        raise HTTPException(409)


### delete


@router.delete("/{anime_id}", status_code=204)
def delete_anime(db: DB, anime_or404: ErrorCheckAnime, anime_id: Annotated[int, Path(ge=1)]) -> None:
    deleted = db.execute("DELETE FROM anime WHERE id = %s", (anime_id,))
    db.commit()
    return deleted


@router.delete("/{anime_id}/genres/{genre_id}", status_code=204)
def delete_animegenre(db: DB, anime: ErrorCheckAnime, genres: ErrorCheckGenre, 
    anime_id: Annotated[int, Path(ge=1)], genre_id: Annotated[int, Path(ge=1)]) -> None:
    deleted = db.execute("DELETE FROM anime_genre WHERE anime_id = %s AND genre_id = %s RETURNING *", (anime_id, genre_id)).fetchone()
    if deleted is None:
        raise HTTPException(404)
    db.commit()



    



        


     
    