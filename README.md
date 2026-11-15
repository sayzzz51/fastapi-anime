# AnimeList API

REST API каталога аниме: тайтлы, жанры, отзывы и рейтинг. Написан на FastAPI и PostgreSQL без ORM — на чистом SQL через psycopg 3.

## Стек

- Python 3.15
- FastAPI
- PostgreSQL + psycopg 3
- Pydantic

## Возможности

- CRUD для аниме, включая частичное обновление через `PATCH`
- Фильтры по статусу, году выхода и жанру (без учёта регистра)
- Пагинация и сортировка через зависимости (`Depends`)
- Связь «многие ко многим» аниме ↔ жанры через связующую таблицу
- Отзывы с оценкой от 1 до 10, средний рейтинг и топ аниме
- Каскадное удаление: вместе с аниме удаляются его отзывы и связи с жанрами
- Корректные HTTP-коды: `201`, `204`, `400`, `404`, `409`, `422`
- Защита от SQL-инъекций: все значения передаются через параметры запроса
- Свой декоратор `@timer` для замера времени выполнения эндпоинтов

## Схема базы данных

```
anime 1 ──── N reviews
  │
  N
  │
anime_genre  (составной первичный ключ: anime_id + genre_id)
  │
  N
  │
genres 1
```

| Таблица | Назначение |
|---|---|
| `anime` | тайтлы: название (уникальное), год, количество серий, статус |
| `genres` | справочник жанров |
| `anime_genre` | связь аниме ↔ жанры, пара не может повторяться |
| `reviews` | отзывы: автор, оценка 1–10, текст (необязательный) |

## Эндпоинты

### Аниме

| Метод | Путь | Описание |
|---|---|---|
| GET | `/anime` | Список аниме. Фильтры: `?status=ongoing&min_year=2010&genre=action`. Пагинация: `?limit=10&offset=0`. Сортировка: `?sort_by=year&order=desc` |
| GET | `/anime/top` | Топ аниме по средней оценке (только с 3+ отзывами) |
| GET | `/anime/{anime_id}` | Одно аниме вместе со списком жанров |
| POST | `/anime` | Добавить аниме |
| PATCH | `/anime/{anime_id}` | Частично изменить аниме |
| DELETE | `/anime/{anime_id}` | Удалить аниме вместе с отзывами и связями |

### Жанры

| Метод | Путь | Описание |
|---|---|---|
| GET | `/genres` | Все жанры |
| POST | `/genres` | Добавить жанр |
| POST | `/anime/{anime_id}/genres/{genre_id}` | Привязать жанр к аниме |
| DELETE | `/anime/{anime_id}/genres/{genre_id}` | Отвязать жанр от аниме |

### Отзывы

| Метод | Путь | Описание |
|---|---|---|
| GET | `/anime/{anime_id}/reviews` | Отзывы аниме с пагинацией |
| POST | `/anime/{anime_id}/reviews` | Оставить отзыв |
| GET | `/anime/{anime_id}/rating` | Средняя оценка и количество отзывов |

### Пример ответа `GET /anime/9`

```json
{
  "id": 9,
  "title": "Death Note",
  "year": 2006,
  "episodes": 37,
  "status": "finished",
  "genres": ["psychological", "thriller", "mystery", "supernatural"]
}
```

## Как запустить

1. Клонировать репозиторий

```bash
git clone https://github.com/sayzzz51/fastapi-anime.git
cd fastapi-anime
```

2. Создать и активировать виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
```

3. Установить зависимости

```bash
pip install -r requirements.txt
```

4. Создать базу данных в PostgreSQL и применить схему

```bash
psql -U postgres -c "CREATE DATABASE anime_db;"
psql -U postgres -d anime_db -f schema.sql
```

5. Создать файл `.env` по примеру `.env.example`

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/anime_db
```

6. Запустить сервер

```bash
uvicorn main:app --reload
```

Документация (Swagger) будет доступна на http://127.0.0.1:8000/docs

## Структура проекта

```
fastapi-anime/
├── main.py             # создание приложения, подключение роутеров
├── db.py               # подключение к PostgreSQL
├── schemas.py          # Pydantic-модели
├── dependencies.py     # зависимости: проверка на 404, пагинация, сортировка
├── routers/
│   ├── __init__.py
│   ├── anime.py        # эндпоинты /anime
│   ├── genres.py       # эндпоинты /genres
│   └── reviews.py      # эндпоинты отзывов
├── schema.sql          # структура базы данных
├── requirements.txt
└── .env.example
```
