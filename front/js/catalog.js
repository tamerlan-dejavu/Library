// Catalog page. The filter form uses method="get", so "Apply" writes the
// filters into the address bar (catalog.html?genre=1&rating=4&q=...).
// On load we read them back, fill the form and ask the API for the books.

const params = new URLSearchParams(location.search);

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

loadFilters();
loadBooks();
