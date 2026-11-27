// Catalog page. The filter form uses method="get", so "Apply" writes the
// filters into the address bar (catalog.html?genre=1&rating=4&q=...).
// On load we read them back, fill the form and ask the API for the books.

const params = new URLSearchParams(location.search);

// Shelves: a genre with its own banner, colours and heading font.
// genreId and count are filled in from /api/filters/ by loadShelves().
const SHELVES = [
  { id: "classic", label: "Classic", genre: "Fiction", title: "Timeless Stories",
    description: "Novels about love, families and society that readers keep coming back to.",
    image: "assets/icon-fiction.png", accent: "#873D35",
    headingFont: '"Cormorant Garamond", serif', titleSize: "2.6rem" },
  { id: "adventure", label: "Adventure", genre: "Sci-Fi", title: "Escape to Another World",
    description: "Spaceships, distant planets and brave explorers for readers who like to travel far.",
    image: "assets/icon-sci-fi.png", accent: "#7A5A12",
    headingFont: '"Source Sans 3", sans-serif', titleSize: "2.2rem" },
  { id: "mystery", label: "Mystery", genre: "Mystery", title: "Every Page Hides a Clue",
    description: "Detectives, locked rooms and secrets. Can you solve the case before the last chapter?",
    image: "assets/icon-mystery.png", accent: "#34495E",
    headingFont: '"Cormorant Garamond", serif', titleSize: "3rem" }
];

// One checkbox per genre, from <template id="genreTemplate">
function showGenres(genres) {
  const box = document.getElementById("genreList");
  const chosen = params.getAll("genre");   // ids (from Home) or names
  box.textContent = "";
  if (genres.length === 0) {
    box.textContent = "No genres yet.";
  }
  for (let i = 0; i < genres.length; i++) {
    const item = document.getElementById("genreTemplate").content.firstElementChild.cloneNode(true);
    const input = item.querySelector("input");
    const label = item.querySelector("label");
    input.id = "genre" + genres[i].id;
    input.value = genres[i].id;
    label.htmlFor = input.id;
    label.textContent = genres[i].name + " (" + genres[i].count + ")";
    for (let j = 0; j < chosen.length; j++) {
      if (chosen[j] === String(genres[i].id) || chosen[j].toLowerCase() === genres[i].name.toLowerCase()) {
        input.checked = true;
      }
    }
    box.appendChild(item);
  }
}

// Puts year, rating and search text from the address back into the form
function fillForm(data) {
  document.getElementById("filterQ").value = params.get("q") || "";
  document.getElementById("yearFrom").value = params.get("year_from") || "";
  document.getElementById("yearTo").value = params.get("year_to") || "";
  if (data.year_min !== null) {
    document.getElementById("yearMin").textContent = data.year_min;
    document.getElementById("yearMax").textContent = data.year_max;
  }
  const rating = params.get("rating") || "";
  const radios = document.querySelectorAll("input[name='rating']");
  for (let i = 0; i < radios.length; i++) {
    radios[i].checked = radios[i].value === rating;
  }
}

async function loadFilters() {
  try {
    const data = await apiRequest("/api/filters/", "GET");
    showGenres(data.genres);
    fillForm(data);
    loadShelves(data.genres);
  } catch (err) {
    showMessage("Could not load the filters. " + err.message, true);
  }
}

// One page link "<", "1", "2", ... from <template id="pageTemplate">
function addPageLink(text, page, label, isCurrent, isDisabled) {
  const item = document.getElementById("pageTemplate").content.firstElementChild.cloneNode(true);
  const link = item.querySelector("a");
  link.textContent = text;
  link.setAttribute("aria-label", label);
  if (isDisabled) {
    item.classList.add("disabled");
    link.setAttribute("aria-disabled", "true");
  } else {
    const copy = new URLSearchParams(params);
    copy.set("page", page);
    link.href = "catalog.html?" + copy.toString();
  }
  if (isCurrent) {
    link.className = "page-link bg-danger border-danger text-white";   // like the reference
    link.setAttribute("aria-current", "page");
  }
  document.getElementById("pager").appendChild(item);
}

// "< 1 2 3 4 5 >": at most 5 numbers around the current page
function showPager(page, pages) {
  document.getElementById("pager").textContent = "";
  if (pages <= 1) {
    return;
  }
  addPageLink("<", page - 1, "Previous page", false, page <= 1);
  const first = Math.max(1, Math.min(page - 2, pages - 4));
  const last = Math.min(pages, first + 4);
  for (let n = first; n <= last; n++) {
    addPageLink(String(n), n, "Page " + n, n === page, false);
  }
  addPageLink(">", page + 1, "Next page", false, page >= pages);
}

// Loads the books for the filters in the address and shows the cards
async function loadBooks() {
  const grid = document.getElementById("bookGrid");
  const q = params.get("q");
  const info = document.getElementById("searchInfo");
  info.textContent = 'Search: "' + q + '"';
  info.classList.toggle("d-none", !q);

  let data;
  try {
    data = await apiRequest("/api/books/?" + params.toString(), "GET");
  } catch (err) {
    grid.textContent = "";
    showMessage("Could not load books. " + err.message, true);
    return;
  }
  grid.textContent = "";
  for (let i = 0; i < data.books.length; i++) {
    grid.appendChild(makeBookCard(data.books[i], true));
  }
  document.getElementById("emptyMessage").classList.toggle("d-none", data.books.length > 0);
  showPager(data.page, data.pages);
}

// After Borrow: load the books again (called from books.js)
function refreshPage() {
  loadBooks();
}

// ---------- shelves ----------

// Finds the genre of every shelf in the database; a shelf without its
// genre is hidden. Then the shelf from the address (?shelf=...) is applied.
function loadShelves(genres) {
  for (let i = 0; i < SHELVES.length; i++) {
    for (let j = 0; j < genres.length; j++) {
      if (genres[j].name === SHELVES[i].genre) {
        SHELVES[i].genreId = String(genres[j].id);
        SHELVES[i].count = genres[j].count;
      }
    }
    const button = document.querySelector("[data-shelf='" + SHELVES[i].id + "']");
    button.classList.toggle("d-none", !SHELVES[i].genreId);
  }
  const shelf = findShelf(params.get("shelf"));
  if (shelf === null || !shelf.genreId) {
    return;
  }
  // The address must hold exactly the genre of the shelf
  const chosen = params.getAll("genre");
  if (chosen.length === 1 && chosen[0] === shelf.genreId) {
    showShelfBanner(shelf);
  } else {
    selectShelf(shelf.id);
  }
}

// The shelf object with this id, or null
function findShelf(id) {
  for (let i = 0; i < SHELVES.length; i++) {
    if (SHELVES[i].id === id) {
      return SHELVES[i];
    }
  }
  return null;
}

// A shelf button was pressed: open the catalog again with only the
// genre of the shelf (and ?shelf=...), the other filters stay
function selectShelf(id) {
  const shelf = findShelf(id);
  const copy = new URLSearchParams(params);
  copy.delete("genre");
  copy.delete("shelf");
  copy.delete("page");
  if (shelf !== null && shelf.genreId) {
    copy.append("genre", shelf.genreId);
    copy.set("shelf", shelf.id);
  }
  location.href = "catalog.html?" + copy.toString();   // "All books" when shelf is null
}

// Banner, colours, heading font and size of the shelf
function showShelfBanner(shelf) {
  const results = document.querySelector(".catalog-results");
  results.dataset.shelf = shelf.id;
  results.style.setProperty("--shelf-accent", shelf.accent);
  results.style.setProperty("--shelf-heading-font", shelf.headingFont);
  results.style.setProperty("--shelf-title-size", shelf.titleSize);

  document.getElementById("shelfImage").src = shelf.image;
  document.getElementById("shelfImage").alt = shelf.label + " shelf";
  document.getElementById("shelfTitle").textContent = shelf.title;
  document.getElementById("shelfDescription").textContent = shelf.description;
  document.getElementById("shelfCount").textContent = shelf.count + " books on this shelf";
  document.getElementById("shelfBanner").classList.remove("d-none");
  markShelfButton(shelf.id);
}

// Removes the banner and the shelf look ("All books"), without reloading
function clearShelf() {
  const results = document.querySelector(".catalog-results");
  delete results.dataset.shelf;
  results.style.removeProperty("--shelf-accent");
  results.style.removeProperty("--shelf-heading-font");
  results.style.removeProperty("--shelf-title-size");
  document.getElementById("shelfBanner").classList.add("d-none");
  markShelfButton("all");
  // also take ?shelf=... out of the address
  const copy = new URLSearchParams(location.search);
  copy.delete("shelf");
  history.replaceState(null, "", "catalog.html?" + copy.toString());
}

// aria-pressed="true" only on the button of this shelf
function markShelfButton(id) {
  const buttons = document.querySelectorAll(".shelf-button");
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute("aria-pressed", String(buttons[i].dataset.shelf === id));
  }
}

// When the genre checkboxes no longer match the shelf, the shelf is reset
function checkShelfGenres() {
  const shelf = findShelf(document.querySelector(".catalog-results").dataset.shelf);
  if (shelf === null) {
    return;
  }
  const checked = document.querySelectorAll("#genreList input:checked");
  if (checked.length !== 1 || checked[0].value !== shelf.genreId) {
    clearShelf();
  }
}

const shelfButtons = document.querySelectorAll(".shelf-button");
for (let i = 0; i < shelfButtons.length; i++) {
  shelfButtons[i].addEventListener("click", function () {
    selectShelf(this.dataset.shelf);   // "all" is not a shelf -> All books
  });
}
document.getElementById("genreList").addEventListener("change", checkShelfGenres);

loadFilters();
loadBooks();
