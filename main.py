from fastapi import FastAPI
from routers import anime, genres, reviews

app = FastAPI()
app.include_router(anime.router)
app.include_router(genres.router)
app.include_router(reviews.router)
