from db import DB
from schemas import AnimeBase, AnimeEdit, Anime, AnimePost, ReviewBase, Review, ReviewPost, Status
from schemas import GenreBase, Genre, GenrePost, timer, AnimeWgenres, anime_with_genres, ReviewWanime
from dependencies import ErrorCheckAnime, ErrorCheckGenre, Pagination, Sorted
from fastapi import FastAPI, Query, Path, HTTPException, Depends, Body, APIRouter
from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row


router = APIRouter(prefix="/reviews", tags=["reviews"])


