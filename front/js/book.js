// Book page: book.html?id=N - details, reviews and the review form

const bookId = new URLSearchParams(location.search).get("id");

// Shows a friendly message instead of the book
function showNotFound(message) {
  document.getElementById("bookArea").classList.add("d-none");
  showBoxMessage("notFound", message);
}

// Adds a small "label: value" line to the details list
function addDetail(list, label, value) {
  const dt = document.createElement("dt");
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.textContent = value;
  list.appendChild(dt);
  list.appendChild(dd);
}

// Draws the list of reviews (newest first, as the API sends them)
function renderReviews(reviews) {
  const list = document.getElementById("reviewList");
  list.textContent = "";

  if (reviews.length === 0) {
    const p = document.createElement("p");
    p.className = "text-muted-ink";
    p.textContent = "No reviews yet. Be the first to write one.";
    list.appendChild(p);
    return;
  }

  for (let i = 0; i < reviews.length; i++) {
    const r = reviews[i];
    const item = document.createElement("article");
    item.className = "review";

    const head = document.createElement("p");
    head.className = "mb-1";
    const name = document.createElement("strong");
    name.textContent = r.author || "Reader";
    head.appendChild(name);

    const meta = document.createElement("span");
    meta.className = "text-muted-ink ms-2";
    // created_at looks like "2026-11-24T08:30:00"; we only need the date
    const date = r.created_at ? r.created_at.slice(0, 10) : "";
    meta.textContent = r.rating + " / 5 · " + date;
    head.appendChild(meta);

    const comment = document.createElement("p");
    comment.className = "mb-0";
    comment.textContent = r.comment || "";

    item.appendChild(head);
    item.appendChild(comment);
    list.appendChild(item);
  }
}

// Loads the book from the API and fills the page.
// Returns the book, or null if it could not be loaded.
async function loadBook() {
  let book;
  try {
    book = await apiGet("/api/books/" + bookId + "/");
  } catch (err) {
    if (err.status === 404) {
      showNotFound("Sorry, we could not find this book.");
    } else {
      showAlert("Could not load the book. " + err.message);
    }
    return null;
  }

  document.title = book.title + " - Book Catalog";

  const coverBox = document.getElementById("coverBox");
  coverBox.textContent = "";
  coverBox.appendChild(createCover(book, "L"));

  document.getElementById("bookTitle").textContent = book.title;
  document.getElementById("bookAuthors").textContent = "by " + book.authors.join(", ");
  document.getElementById("bestsellerBadge").classList.toggle("d-none", !book.is_bestseller);

  const details = document.getElementById("bookDetails");
  details.textContent = "";
  addDetail(details, "Genre", book.genre || "No genre");
  addDetail(details, "Year", book.year || "Unknown");
  addDetail(details, "Rating", ratingText(book.rating));
  addDetail(details, "Copies on the shelf", book.available_copies);

  document.getElementById("bookDescription").textContent = book.description || "";

  // Reload the whole book after borrowing, so the copies update
  const buttonBox = document.getElementById("borrowBox");
  buttonBox.textContent = "";
  buttonBox.appendChild(createBorrowButton(book, loadBook));

  renderReviews(book.reviews);
  return book;
}

// First load of the page: the book, then the Open Library card
// (only once, not after every borrow or review)
async function startPage() {
  const book = await loadBook();
  if (book !== null) {
    loadOpenLibrary(book);
  }
}

// Shows the review form only to logged-in users
async function setupReviewForm() {
  let me;
  try {
    me = await apiGet("/api/me/");
  } catch (err) {
    showAlert("Could not check your account. " + err.message);
    return;
  }

  document.getElementById("reviewForm").classList.toggle("d-none", !me.logged_in);
  document.getElementById("signInToReview").classList.toggle("d-none", me.logged_in);
}

// Sends the review form to the API, then reloads the reviews
async function submitReview() {
  const form = document.getElementById("reviewForm");
  hideBoxMessage("reviewError");

  try {
    await apiPost("/api/books/" + bookId + "/reviews/", {
      rating: parseInt(form.elements["rating"].value),
      comment: form.elements["comment"].value.trim()
    });
  } catch (err) {
    // e.g. "You have already reviewed this book."
    showBoxMessage("reviewError", err.message);
    return;
  }

  form.reset();
  showAlert("Thank you, your review was saved.", "secondary");
  loadBook();
}

// DOMContentLoaded waits until every script (also openlibrary.js) is loaded
document.addEventListener("DOMContentLoaded", function () {
  if (bookId === null || bookId === "") {
    showNotFound("No book was selected. Please choose one in the catalog.");
  } else {
    startPage();
    setupReviewForm();
  }
});
