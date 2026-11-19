from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routers import anime, genres

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anime.router)
app.include_router(genres.router)
