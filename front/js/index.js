// Home page: the "Reading mood" hero, the book list and the genre tiles

// Pictures for the genres we have icons for; other genres show their first letter
const GENRE_ICONS = {
  "fiction": "assets/icon-fiction.png",
  "non-fiction": "assets/icon-non-fiction.png",
  "sci-fi": "assets/icon-sci-fi.png",
  "biography": "assets/icon-biography.png",
  "fantasy": "assets/icon-novel.png",
  "mystery": "assets/icon-mystery.png"
};

// One simple object per reading mood
const MOODS = {
  classic: {
    slogan: "Your Next Great Read Is Waiting",
    description: "Timeless novels about love, society and people. Borrow a classic and see why readers still return to it.",
    image: "assets/icon-fiction.png", accent: "#873D35", accentNight: "#A04A40",
    headingFont: '"Cormorant Garamond", serif', titleSize: "3rem",
    genre: "Fiction", booksTitle: "Classic picks"
  },
  adventure: {
    slogan: "Escape to Another World",
    description: "Spaceships, distant planets and brave explorers. Science fiction for readers who like to travel far.",
    image: "assets/icon-sci-fi.png", accent: "#7A5A12", accentNight: "#8A6614",
    headingFont: '"Source Sans 3", sans-serif', titleSize: "2.6rem",
    genre: "Sci-Fi", booksTitle: "Adventure picks"
  },
  mystery: {
    slogan: "Every Page Hides a Clue",
    description: "Detectives, locked rooms and secrets. Pick a mystery and try to solve the case before the last chapter.",
    image: "assets/icon-mystery.png", accent: "#34495E", accentNight: "#4A6582",
    headingFont: '"Cormorant Garamond", serif', titleSize: "3.4rem",
    genre: "Mystery", booksTitle: "Mystery picks"
  }
};

let currentMood = null;   // the mood shown now

// The saved mood, or "classic" (localStorage can be blocked)
function loadMood() {
  try {
    const name = localStorage.getItem("mood");
    if (MOODS[name]) {
      return name;
    }
  } catch (err) {
    // ignore: use the default
  }
  return "classic";
}

// Changes the texts, the picture and the look of the hero, then the books
function applyMood(name) {
  const mood = MOODS[name];
  const hero = document.getElementById("hero");
  currentMood = mood;
  document.getElementById("moodSlogan").textContent = mood.slogan;
  document.getElementById("moodDescription").textContent = mood.description;
  document.getElementById("moodImage").src = mood.image;
  document.getElementById("moodImage").alt = mood.genre + " books";
  hero.style.setProperty("--mood-accent", mood.accent);
  hero.style.setProperty("--mood-accent-night", mood.accentNight);
  hero.style.setProperty("--mood-heading-font", mood.headingFont);
  hero.style.setProperty("--mood-title-size", mood.titleSize);

  const buttons = document.querySelectorAll("[data-mood]");
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute("aria-pressed", String(buttons[i].dataset.mood === name));
  }
  loadBooksForMood(mood);
}

// A mood button was pressed: remember the choice and show it
function setMood(name) {
  try {
    localStorage.setItem("mood", name);
  } catch (err) {
    // ignore: the mood still changes on this page
  }
  applyMood(name);
}

// Books of the mood's genre; fewer than 5 (or no such genre) -> bestsellers
async function loadBooksForMood(mood) {
  let books = [];
  let title = mood.booksTitle;
  try {
    const filters = await apiRequest("/api/filters/", "GET");
    for (let i = 0; i < filters.genres.length; i++) {
      if (filters.genres[i].name === mood.genre) {
        books = (await apiRequest("/api/books/?genre=" + filters.genres[i].id, "GET")).books;
      }
    }
    if (books.length < 5) {
      title = "Bestsellers";
      books = (await apiRequest("/api/books/?bestseller=1", "GET")).books;
    }
  } catch (err) {
    showMessage("Could not load books. " + err.message, true);
  }
  // Another mood was chosen while we waited: its own list will come
  if (mood === currentMood) {
    showBooks(books, title);
  }
}

// Shows the first 5 books under the given title
function showBooks(books, title) {
  const grid = document.getElementById("bestsellers");
  document.getElementById("bestsellersTitle").textContent = title;
  grid.textContent = "";
  if (books.length === 0) {
    grid.textContent = "No books yet.";
  }
  for (let i = 0; i < books.length && i < 5; i++) {
    grid.appendChild(makeBookCard(books[i], false));
  }
}

// One tile per genre from the database: picture or letter, name, count
async function loadCategories() {
  const box = document.getElementById("categories");
  let data;
  try {
    data = await apiRequest("/api/filters/", "GET");
  } catch (err) {
    box.textContent = "";
    showMessage("Could not load the genres. " + err.message, true);
    return;
  }
  box.textContent = "";
  if (data.genres.length === 0) {
    box.textContent = "No genres yet.";
  }
  for (let i = 0; i < data.genres.length; i++) {
    box.appendChild(makeCategoryTile(data.genres[i]));
  }
}

// Makes one tile from <template id="categoryTemplate">
function makeCategoryTile(genre) {
  const tile = document.getElementById("categoryTemplate").content.firstElementChild.cloneNode(true);
  const icon = GENRE_ICONS[genre.name.toLowerCase()];
  tile.href = "catalog.html?genre=" + genre.id;
  if (icon) {
    tile.querySelector(".category-icon").src = icon;
    tile.querySelector(".category-letter").remove();
  } else {
    tile.querySelector(".category-icon").remove();
    tile.querySelector(".category-letter").textContent = genre.name.charAt(0);
  }
  tile.querySelector(".category-name").textContent = genre.name;
  tile.querySelector(".category-count").textContent = genre.count + (genre.count === 1 ? " book" : " books");
  return tile;
}

// After Borrow: load the books of the current mood again (called from books.js)
function refreshPage() {
  loadBooksForMood(MOODS[loadMood()]);
}

// Mood buttons; each keeps its mood name in data-mood
const moodButtons = document.querySelectorAll("[data-mood]");
for (let i = 0; i < moodButtons.length; i++) {
  moodButtons[i].addEventListener("click", function () {
    setMood(this.dataset.mood);
  });
}

applyMood(loadMood());
loadCategories();
