from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
from fastapi import Depends, Query, Path, HTTPException
from dependencies import ErrorCheckAnime, ErrorCheckGenre, Pagination, Sorted
from db import DB
from functools import wraps 
import time

###anime schemas 
Status = Literal["ongoing", "finished", "announced"]

class AnimeBase(BaseModel):
    title: Annotated[str, Field(max_length=200)] 
    year: Annotated[int, Field(ge=1960, le=2026)]
    episodes: Annotated[int, Field(ge=1)]
    status: Status

class AnimePost(AnimeBase):
    pass

class AnimeEdit(BaseModel):
    title: Annotated[str, Field(max_length=200)] | None = None
    year: Annotated[int, Field(ge=1960, le=2026)] | None = None
    episodes: Annotated[int, Field(ge=1)] | None = None
    status: Status | None = None

class Anime(AnimeBase):
    id: Annotated[int, Field(ge=1)]

class AnimeWgenres(Anime):
    genres: List[str]

class AnimeRating(BaseModel):
    anime_id: Annotated[int, Field(ge=1)]
    review_count: Annotated[int, Field(ge=0)]
    average_score: float | None

class AnimeTop(Anime):
    review_count: Annotated[int, Field(ge=0)]
    average_score: float | None
    
    
##genres schemas

class GenreBase(BaseModel):
    name: Annotated[str, Field(max_length=50)]

class GenrePost(GenreBase):
    pass

class Genre(GenreBase):
    id: Annotated[int, Field(ge=1)]


###review schemas 

class ReviewBase(BaseModel):
    anime_id: Annotated[int, Field(ge=1)]
    author: Annotated[str, Field(max_length=50)]
    score: Annotated[int, Field(ge=1,le=10)]
    text: Annotated[str, Field(max_length=1000)] | None

class ReviewPost(ReviewBase):
    pass

class Review(ReviewBase):
    id: Annotated[int, Field(ge=1)]

class ReviewWanime(BaseModel):
    anime: Annotated[str, Field(max_length=200)]
    author: Annotated[str, Field(max_length=50)]
    score: Annotated[int, Field(ge=1,le=10)]
    text: Annotated[str, Field(max_length=1000)] | None
    

# декоратор_таймер 
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Выполняю {func.__name__}")
        res = func(*args, **kwargs)
        end = time.time() - start 
        print(f"Выполнение заняло {end} сек")
        return res
    return wrapper


### крутая функция для словаря аниме + его жанров
def anime_with_genres(db: DB, anime_id: Annotated[int, Path(ge=1)]) -> List:
    get_genre = db.execute("SELECT genres.name FROM genres LEFT JOIN anime_genre ON anime_genre.genre_id = genres.id WHERE anime_genre.anime_id = %s",(anime_id,)).fetchall()
    genre_names = [row["name"] for row in get_genre]
    return genre_names

