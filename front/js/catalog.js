// Catalog page. The filter form uses method="get", so "Apply" writes the
// filters into the address bar (catalog.html?genre=1&rating=4&q=...).
// On load we read them back, fill the form and ask the API for the books.

const params = new URLSearchParams(location.search);

// Genre checkboxes built from /api/filters/ (one per genre in the database)
function renderGenres(genres) {
  const box = document.getElementById("genreList");
  box.textContent = "";
  // The URL may hold genre ids (from Home) or names
  const chosen = params.getAll("genre").map(function (g) { return g.toLowerCase(); });

  for (let i = 0; i < genres.length; i++) {
    const g = genres[i];
    const id = "genre" + g.id;
    const input = el("input", { className: "form-check-input", type: "checkbox",
                                name: "genre", value: String(g.id), id: id });
    input.checked = chosen.includes(String(g.id)) || chosen.includes(g.name.toLowerCase());
    box.appendChild(el("div", { className: "form-check" }, [
      input,
      el("label", { className: "form-check-label", for: id, text: g.name + " (" + g.count + ")" })
    ]));
  }
  if (genres.length === 0) {
    box.appendChild(el("p", { className: "text-body-secondary mb-0", text: "No genres yet." }));
  }
}

// Puts year, rating and search text from the URL back into the form
function fillFilters(data) {
  document.getElementById("filterQ").value = params.get("q") || "";
  const yearFrom = document.getElementById("yearFrom");
  const yearTo = document.getElementById("yearTo");
  yearFrom.value = params.get("year_from") || "";
  yearTo.value = params.get("year_to") || "";

  // Smallest and largest year in the database, shown under the fields
  if (data.year_min !== null) {
    yearFrom.min = yearTo.min = data.year_min;
    yearFrom.max = yearTo.max = data.year_max;
    document.getElementById("yearMin").textContent = data.year_min;
    document.getElementById("yearMax").textContent = data.year_max;
  }

  const rating = params.get("rating") || "";
  const radio = document.querySelector("input[name='rating'][value='" + CSS.escape(rating) + "']");
  (radio || document.getElementById("ratingAny")).checked = true;
}

async function loadFilters() {
  try {
    const data = await apiGet("/api/filters/");
    renderGenres(data.genres);
    fillFilters(data);
  } catch (err) {
    showAlert("Could not load the filters. " + err.message);
  }
}

// Returns a catalog URL with the same filters but another page
function pageUrl(page) {
  const copy = new URLSearchParams(params);
  copy.set("page", page);
  return "catalog.html?" + copy.toString();
}

// "< 1 2 3 4 5 >": at most 5 page numbers around the current page
function renderPager(page, pages) {
  const list = document.getElementById("pager");
  list.textContent = "";
  if (pages <= 1) {
    return;
  }

  // Previous / next: a link, or a disabled box on the first / last page
  function arrow(text, target, label) {
    if (target < 1 || target > pages) {
      return el("li", { className: "page-item disabled" }, [
        el("span", { className: "page-link", "aria-label": label, text: text })
      ]);
    }
    return el("li", { className: "page-item" }, [
      el("a", { className: "page-link text-danger", href: pageUrl(target), "aria-label": label, text: text })
    ]);
  }

  list.appendChild(arrow("<", page - 1, "Previous page"));
  const first = Math.max(1, Math.min(page - 2, pages - 4));
  const last = Math.min(pages, first + 4);
  for (let n = first; n <= last; n++) {
    const link = el("a", { className: "page-link text-danger", href: pageUrl(n),
                           "aria-label": "Page " + n, text: String(n) });
    if (n === page) {
      // the current page: red box, like the reference
      link.className = "page-link bg-danger border-danger text-white";
      link.setAttribute("aria-current", "page");
    }
    list.appendChild(el("li", { className: "page-item" }, [link]));
  }
  list.appendChild(arrow(">", page + 1, "Next page"));
}

// Loads the books for the filters in the URL and draws the cards
async function loadBooks() {
  const grid = document.getElementById("bookGrid");
  const empty = document.getElementById("emptyMessage");
  const q = params.get("q");
  const info = document.getElementById("searchInfo");
  info.textContent = q ? 'Search: "' + q + '"' : "";
  info.classList.toggle("d-none", !q);

  let data;
  try {
    data = await apiGet("/api/books/?" + params.toString());
  } catch (err) {
    grid.textContent = "";
    showAlert("Could not load books. " + err.message);
    return;
  }

  grid.textContent = "";
  for (let i = 0; i < data.books.length; i++) {
    grid.appendChild(createBookCard(data.books[i], { showBadge: true, afterBorrow: loadBooks }));
  }
  empty.classList.toggle("d-none", data.books.length > 0);
  renderPager(data.page, data.pages);
}

loadFilters();
loadBooks();
