from typing import List, Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Path
from functools import wraps 
import time
from models import GenresORM, AnimeGenreORM
from sqlalchemy import select
from sqlalchemy.orm import Session

###anime schemas 
Status = Literal["ongoing", "finished", "announced"]

class AnimeBase(BaseModel):
    title: Annotated[str, Field(max_length=200)] 
    year: Annotated[int, Field(ge=1960, le=2030)]
    episodes: Annotated[int, Field(ge=1)]
    status: Status

class AnimePost(AnimeBase):
    pass

class AnimeEdit(BaseModel):
    title: Annotated[str, Field(max_length=200)] | None = None
    year: Annotated[int, Field(ge=1960, le=2030)] | None = None
    episodes: Annotated[int, Field(ge=1)] | None = None
    status: Status | None = None

class Anime(AnimeBase):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(ge=1)]

class AnimeWgenres(Anime):
    genres: List[str]

class AnimeRating(BaseModel):
    anime_id: Annotated[int, Field(ge=1)]
    review_count: Annotated[int, Field(ge=0)]
    average_score: float | None

class AnimeTop(Anime):
    model_config = ConfigDict(from_attributes=True)
    review_count: Annotated[int, Field(ge=0)]
    average_score: float | None
    
    
##genres schemas

class GenreBase(BaseModel):
    name: Annotated[str, Field(max_length=50)]

class GenrePost(GenreBase):
    pass

class Genre(GenreBase):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(ge=1)]


###review schemas 

class ReviewBase(BaseModel):
    
    author: Annotated[str, Field(max_length=50)]
    score: Annotated[int, Field(ge=1,le=10)]
    text: Annotated[str, Field(max_length=1000)] | None = None

class ReviewPost(ReviewBase):
    pass

class Review(ReviewBase):
    id: Annotated[int, Field(ge=1)]
    anime_id: Annotated[int, Field(ge=1)]

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
        print(f"Выполнение заняло {round(end,4)} сек")
        return res
    return wrapper


### крутая функция для словаря аниме + его жанров
def anime_with_genres(db: Session, anime_id: Annotated[int, Path(ge=1)]) -> List:
    get_genre = (select(GenresORM.name)
                .join(AnimeGenreORM, AnimeGenreORM.genre_id == GenresORM.id)
                .where(AnimeGenreORM.anime_id == anime_id))
    return db.scalars(get_genre).all()

