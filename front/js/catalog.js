// Catalog page. The filter form uses method="get", so pressing "Apply"
// writes the filters into the URL (catalog.html?genre=...&q=...).
// On load we read them back from the URL and ask the API for those books.

// Puts the values from the URL back into the filter form
function fillFiltersFromUrl(params) {
  const form = document.getElementById("filterForm");

  // genre can appear several times: ?genre=Fantasy&genre=Sci-Fi
  const genres = params.getAll("genre").map(function (g) {
    return g.toLowerCase();
  });
  const boxes = form.querySelectorAll("input[name='genre']");
  for (let i = 0; i < boxes.length; i++) {
    boxes[i].checked = genres.includes(boxes[i].value.toLowerCase());
  }

  form.elements["year_from"].value = params.get("year_from") || "";
  form.elements["year_to"].value = params.get("year_to") || "";
  form.elements["rating"].value = params.get("rating") || "";
  form.elements["q"].value = params.get("q") || "";
}

// Returns a catalog URL with the same filters but another page number
function pageUrl(params, page) {
  const copy = new URLSearchParams(params);
  copy.set("page", page);
  return "catalog.html?" + copy.toString();
}

// Draws Previous / "Page X of Y" / Next
function renderPager(params, page, pages) {
  const prev = document.getElementById("prevPage");
  const next = document.getElementById("nextPage");

  document.getElementById("pageInfo").textContent = "Page " + page + " of " + pages;

  // A disabled link: no href, and Bootstrap's "disabled" look
  prev.classList.toggle("disabled", page <= 1);
  next.classList.toggle("disabled", page >= pages);
  prev.href = page > 1 ? pageUrl(params, page - 1) : "#";
  next.href = page < pages ? pageUrl(params, page + 1) : "#";
}

// Loads the books for the filters in the URL and draws the cards
async function loadBooks() {
  const params = new URLSearchParams(location.search);
  const grid = document.getElementById("bookGrid");
  const empty = document.getElementById("emptyMessage");

  let data;
  try {
    // The page URL already has the right query string for the API
    data = await apiGet("/api/books/?" + params.toString());
  } catch (err) {
    grid.textContent = "";
    showAlert("Could not load books. " + err.message);
    return;
  }

  grid.textContent = "";
  for (let i = 0; i < data.books.length; i++) {
    grid.appendChild(createBookCard(data.books[i], loadBooks));
  }

  empty.classList.toggle("d-none", data.books.length > 0);
  renderPager(params, data.page, data.pages);
}

fillFiltersFromUrl(new URLSearchParams(location.search));
loadBooks();
