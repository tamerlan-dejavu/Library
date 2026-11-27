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

// First 5 books with is_bestseller from the API
async function loadBestsellers() {
  const grid = document.getElementById("bestsellers");
  let data;
  try {
    data = await apiGet("/api/books/?bestseller=1");
  } catch (err) {
    grid.textContent = "";
    showAlert("Could not load bestsellers. " + err.message);
    return;
  }

  grid.textContent = "";
  const books = data.books.slice(0, 5);
  if (books.length === 0) {
    grid.appendChild(el("p", { className: "col", text: "No bestsellers yet." }));
  }
  for (let i = 0; i < books.length; i++) {
    grid.appendChild(createBookCard(books[i], { afterBorrow: loadBestsellers }));
  }
}

// One tile per genre from the database (picture or letter, name, count)
async function loadCategories() {
  const box = document.getElementById("categories");
  let data;
  try {
    data = await apiGet("/api/filters/");
  } catch (err) {
    box.textContent = "";
    showAlert("Could not load the genres. " + err.message);
    return;
  }

  box.textContent = "";
  if (data.genres.length === 0) {
    box.appendChild(el("p", { className: "col", text: "No genres yet." }));
  }
  for (let i = 0; i < data.genres.length; i++) {
    const genre = data.genres[i];
    const icon = GENRE_ICONS[genre.name.toLowerCase()];
    const picture = icon
      ? el("img", { src: icon, alt: "", className: "w-100 object-fit-cover mb-2" })
      : el("span", { className: "d-block category-letter mb-2", "aria-hidden": "true", text: genre.name.charAt(0) });
    const books = genre.count === 1 ? "1 book" : genre.count + " books";

    box.appendChild(el("div", { className: "col" }, [
      el("a", { href: "catalog.html?genre=" + genre.id,
                className: "d-block h-100 bg-secondary-subtle text-body text-decoration-none text-center p-3 category-tile" }, [
        picture,
        el("p", { className: "mb-0", text: genre.name }),
        el("p", { className: "mb-0 small text-body-secondary", text: books })
      ])
    ]));
  }
}

loadBestsellers();
loadCategories();
