from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
from fastapi import Depends, Query, Path, HTTPException
from db import DB

### проверка на 404
def except404_anime(db: DB, anime_id: Annotated[int, Path(ge=1)]) -> Dict:
    response = db.execute("SELECT * FROM anime WHERE id = %s", (anime_id,)).fetchone()
    if response is None:
        raise HTTPException(status_code=404, detail=f"Элемента с id {anime_id} не найдено")
    return response 

ErrorCheckAnime = Annotated[Dict, Depends(except404_anime)]


def except404_genre(db: DB, genre_id: Annotated[int, Path(ge=1)]) -> Dict:
    response = db.execute("SELECT * FROM genres WHERE id = %s", (genre_id,)).fetchone()
    if response is None:
        raise HTTPException(status_code=404, detail=f"Элемента с id {genre_id} не найдено")
    return response 

ErrorCheckGenre = Annotated[Dict, Depends(except404_genre)]

### пагинация
class PaginationParams(BaseModel):
    offset: Annotated[int, Field(ge=0)] = 0 
    limit: Annotated[int, Field(le=100)] = 10 

Pagination = Annotated[PaginationParams, Query()]

### сортировка
Sort = Literal["id", "year", "title"]
Order = Literal["ASC", "DESC"]
def sort(db: DB, sort_by: Sort = "id", order_by: Order = "ASC") -> str:
    sorted = (f" ORDER BY anime.{sort_by} {order_by}")
    return sorted

Sorted = Annotated[str, Depends(sort)]

