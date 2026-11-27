// Home page: 5 bestsellers and the genre tiles

// Pictures for the genres we have icons for; other genres show their first letter
const GENRE_ICONS = {
  "fiction": "assets/icon-fiction.png",
  "non-fiction": "assets/icon-non-fiction.png",
  "sci-fi": "assets/icon-sci-fi.png",
  "biography": "assets/icon-biography.png",
  "fantasy": "assets/icon-novel.png",
  "mystery": "assets/icon-mystery.png"
};

// Loads the first 5 bestsellers (books with a cover come first)
async function loadBestsellers() {
  const grid = document.getElementById("bestsellers");
  let data;
  try {
    data = await apiRequest("/api/books/?bestseller=1", "GET");
  } catch (err) {
    grid.textContent = "";
    showMessage("Could not load bestsellers. " + err.message, true);
    return;
  }

  grid.textContent = "";
  if (data.books.length === 0) {
    grid.textContent = "No bestsellers yet.";
  }
  for (let i = 0; i < data.books.length && i < 5; i++) {
    grid.appendChild(makeBookCard(data.books[i], false));
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
  if (genre.count === 1) {
    tile.querySelector(".category-count").textContent = "1 book";
  } else {
    tile.querySelector(".category-count").textContent = genre.count + " books";
  }
  return tile;
}

// After Borrow: load the bestsellers again (called from books.js)
function refreshPage() {
  loadBestsellers();
}

loadBestsellers();
loadCategories();
