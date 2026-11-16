const LIMIT = 8;
let offset = 0;
const API = "http://127.0.0.1:8000";

async function loadTop() {
  const response = await fetch(`${API}/anime/top`);
  const data = await response.json();
  console.log(data);
  const list = document.querySelector("#top-list");
  list.innerHTML = "";
const template = document.querySelector("#top-item");

for (const anime of data) {
  const item = template.content.cloneNode(true);   // копия шаблона

  item.querySelector(".top-title").textContent = anime.title;
  item.querySelector(".top-score").textContent = anime.average_score;
  item.querySelector(".top-count").textContent = `${anime.review_count} оценок`;
  item.querySelector("a").href = `anime.html?id=${anime.id}`;
 

  list.append(item);          
  
}
}

loadTop();



async function loadGenres() {
  const response = await fetch(`${API}/genres`);
  const genres = await response.json();
  const select = document.querySelector("#genre");

  for (const genre of genres) {
    const option = document.createElement("option");   // создать новый <option>
    option.textContent = genre.name;   
    option.value = genre.name
    select.append(option);
  }
}

loadGenres();



const STATUS_LABELS = {
  ongoing: "Выходит",
  finished: "Вышло",
  announced: "Анонс",
};

async function loadAnime(params) {    
  params.set("limit", LIMIT);
  params.set("offset", offset);                          // ← добавил params
  const response = await fetch(`${API}/anime?${params}`);       // ← добавил ?${params}
  const animeList = await response.json();

  const list = document.querySelector("#anime-list");
  list.innerHTML = "";                                          // ← очистка полки
  const template = document.querySelector("#anime-card");

  for (const anime of animeList) {
    const item = template.content.cloneNode(true);
    const title = item.querySelector(".spine-title");
    title.textContent = anime.title;  
    const year = item.querySelector(".spine-year");
    year.textContent = anime.year;  
    const status = item.querySelector(".spine-status");
    status.textContent = STATUS_LABELS[anime.status];;  
    item.querySelector("a").href = `anime.html?id=${anime.id}`;   
    item.querySelector(".spine").dataset.status = anime.status;
    list.append(item);
  }
  document.querySelector("#empty").hidden = animeList.length > 0;
  document.querySelector("#prev-page").disabled = offset === 0;
document.querySelector("#next-page").disabled = animeList.length < LIMIT;
document.querySelector("#page-number").textContent = `Страница ${offset / LIMIT + 1}`;
}

loadAnime(new URLSearchParams());



const form = document.querySelector("#filters");


form.addEventListener("reset", () => {
  offset = 0;
  loadAnime(new URLSearchParams());
});

function getFilterParams() {
  const params = new URLSearchParams(new FormData(form));
  for (const [key, value] of [...params]) {
    if (value === "") {
      params.delete(key);
    }
  }
  return params;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  offset = 0;
  loadAnime(getFilterParams());
});

document.querySelector("#next-page").addEventListener("click", () => {
  offset = offset + LIMIT;
  loadAnime(getFilterParams());
});

document.querySelector("#prev-page").addEventListener("click", () => {
  offset = offset - LIMIT;
  loadAnime(getFilterParams());
});

