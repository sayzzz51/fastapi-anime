const API = "http://127.0.0.1:8000";
const REVIEWS_LIMIT = 5;
let reviewsOffset = 0;

const STATUS_LABELS = {
  ongoing: "Выходит",
  finished: "Вышло",
  announced: "Анонс",
};

// id из адреса: anime.html?id=9 → "9"
const animeId = new URLSearchParams(window.location.search).get("id");

// ---------- 1. Аниме ----------

async function loadAnime() {
  const response = await fetch(`${API}/anime/${animeId}`);

  // 404 или кривой id → показываем заглушку и прячем остальное
  if (!response.ok) {
    document.querySelector("#anime").hidden = true;
    document.querySelector(".reviews-layout").hidden = true;
    document.querySelector("#page-error").hidden = false;
    return false;
  }

  const anime = await response.json();

  document.title = `${anime.title} — AnimeList`;
  document.querySelector("#title").textContent = anime.title;
  document.querySelector("#cover-title").textContent = anime.title;
  document.querySelector("#cover").dataset.status = anime.status;
  document.querySelector("#year").textContent = anime.year;
  document.querySelector("#episodes").textContent = anime.episodes;
  document.querySelector("#status").textContent = STATUS_LABELS[anime.status];

  const genresList = document.querySelector("#genres");
  genresList.innerHTML = "";
  for (const genre of anime.genres) {
    const li = document.createElement("li");
    li.textContent = genre;
    genresList.append(li);
  }

  return true;
}

// ---------- 2. Рейтинг ----------

async function loadRating() {
  const response = await fetch(`${API}/anime/${animeId}/rating`);
  if (!response.ok) return;

  const rating = await response.json();
  const score = document.querySelector("#rating-score");
  const count = document.querySelector("#rating-count");

  // average_score = null, когда отзывов нет (AVG вернул NULL)
  if (rating.average_score === null) {
    score.textContent = "—";
    count.textContent = "Оценок пока нет";
  } else {
    score.textContent = rating.average_score;
    count.textContent = `по ${rating.review_count} ${pluralReviews(rating.review_count)}`;
  }
}

// «по 1 отзыву», «по 3 отзывам» — склонение для русского
function pluralReviews(n) {
  return n % 10 === 1 && n % 100 !== 11 ? "отзыву" : "отзывам";
}

// ---------- 3. Отзывы ----------

async function loadReviews() {
  const params = new URLSearchParams({ limit: REVIEWS_LIMIT, offset: reviewsOffset });
  const response = await fetch(`${API}/anime/${animeId}/reviews?${params}`);
  if (!response.ok) return;

  const reviews = await response.json();
  const list = document.querySelector("#review-list");
  const template = document.querySelector("#review-item");
  list.innerHTML = "";

  for (const review of reviews) {
    const item = template.content.cloneNode(true);
    item.querySelector(".review-score").textContent = review.score;
    item.querySelector(".review-author").textContent = review.author;
    // text может быть null — тогда абзац пустой, и CSS его прячет
    item.querySelector(".review-text").textContent = review.text ?? "";
    list.append(item);
  }

  const isFirstPage = reviewsOffset === 0;
  document.querySelector("#reviews-empty").hidden = !(isFirstPage && reviews.length === 0);
  document.querySelector("#reviews-prev").disabled = isFirstPage;
  document.querySelector("#reviews-next").disabled = reviews.length < REVIEWS_LIMIT;
  document.querySelector("#reviews-page").textContent = `Страница ${reviewsOffset / REVIEWS_LIMIT + 1}`;
}

document.querySelector("#reviews-next").addEventListener("click", () => {
  reviewsOffset += REVIEWS_LIMIT;
  loadReviews();
});

document.querySelector("#reviews-prev").addEventListener("click", () => {
  reviewsOffset -= REVIEWS_LIMIT;
  loadReviews();
});

// ---------- 4. Форма отзыва ----------

const form = document.querySelector("#review-form");
const message = document.querySelector("#form-message");

function showMessage(text, type) {
  message.textContent = text;
  message.dataset.type = type;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const author = formData.get("author").trim();
  const score = formData.get("score"); // null, если оценка не выбрана
  const text = formData.get("text").trim();

  // Проверяем до отправки, чтобы не гонять запрос зря
  if (!author) {
    showMessage("Укажите имя.", "error");
    return;
  }
  if (!score) {
    showMessage("Выберите оценку от 1 до 10.", "error");
    return;
  }

  const response = await fetch(`${API}/anime/${animeId}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      author: author,
      score: Number(score),
      text: text || null, // пустой текст отправляем как null
    }),
  });

  if (response.status === 201) {
    showMessage("Отзыв опубликован.", "success");
    form.reset();
    reviewsOffset = 0;
    loadRating();
    loadReviews();
  } else if (response.status === 404) {
    showMessage("Это аниме удалили, отзыв не сохранён.", "error");
  } else if (response.status === 422) {
    showMessage("Проверьте поля: имя до 50 символов, текст до 1000.", "error");
  } else {
    showMessage("Сервер не ответил. Попробуйте ещё раз.", "error");
  }
});

// ---------- Старт ----------

async function init() {
  const exists = await loadAnime();
  if (!exists) return; // аниме нет — рейтинг и отзывы не грузим
  loadRating();
  loadReviews();
}

init();