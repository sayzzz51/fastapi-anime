from typing import Annotated, Literal
from pydantic import BaseModel, Field
from fastapi import Depends, Query, Path, HTTPException
from db import DB
from models import AnimeORM, GenresORM

### проверка на 404
def except404_anime(db: DB, anime_id: Annotated[int, Path(ge=1)]) -> AnimeORM:
    response = db.get(AnimeORM, anime_id)
    if response is None:
        raise HTTPException(status_code=404, detail=f"Элемента с id {anime_id} не найдено")
    return response 

ErrorCheckAnime = Annotated[AnimeORM, Depends(except404_anime)]


def except404_genre(db: DB, genre_id: Annotated[int, Path(ge=1)]) -> GenresORM:
    response = db.get(GenresORM, genre_id)
    if response is None:
        raise HTTPException(status_code=404, detail=f"Элемента с id {genre_id} не найдено")
    return response 

ErrorCheckGenre = Annotated[GenresORM, Depends(except404_genre)]

### пагинация
class PaginationParams(BaseModel):
    offset: Annotated[int, Field(ge=0)] = 0 
    limit: Annotated[int, Field(le=100)] = 10 

Pagination = Annotated[PaginationParams, Query()]

### сортировка
class SortParams(BaseModel):

    sort : Literal["id", "year", "title"] = "id"
    order: Literal["ASC", "DESC"] = "ASC"


Sorting = Annotated[SortParams, Query()]


class OrderParams(BaseModel):
    order: Literal["ASC", "DESC"] = "ASC"


OrderOnly = Annotated[OrderParams, Query()]

