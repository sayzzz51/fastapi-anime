from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class AnimeORM(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)
    year: Mapped[int]
    episodes: Mapped[int]
    status: Mapped[str] = mapped_column(String(20))

class GenresORM(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

class AnimeGenreORM(Base):
    __tablename__ = "anime_genre"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)

class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id", ondelete="CASCADE"))
    author: Mapped[str] = mapped_column(String(50))
    score: Mapped[int]
    text: Mapped[str | None] = mapped_column(String(1000))