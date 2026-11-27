// Book page: book.html?id=N - details, reviews and the review form

const bookId = new URLSearchParams(location.search).get("id");

// Shows a friendly message instead of the book
function showNotFound(message) {
  document.getElementById("bookArea").classList.add("d-none");
  showBoxMessage("notFound", message);
}

// Yellow stars with a text for screen readers, e.g. "4 out of 5 stars"
function makeStars(rating) {
  return el("span", { className: "stars", role: "img", "aria-label": rating + " out of 5 stars",
                      text: starsText(rating) });
}

// "2026-11-24T08:30:00" -> "2026-11-24"
function shortDate(value) {
  return value ? value.slice(0, 10) : "";
}

// Draws the list of reviews (newest first, as the API sends them)
function renderReviews(reviews) {
  const list = document.getElementById("reviewList");
  list.textContent = "";

  if (reviews.length === 0) {
    list.appendChild(el("p", { text: "No reviews yet. Be the first to write one." }));
    return;
  }

  for (let i = 0; i < reviews.length; i++) {
    const r = reviews[i];
    list.appendChild(el("article", {
      className: "card card-body bg-secondary-subtle border-0 border-top border-3 border-danger mb-3"
    }, [
      el("div", { className: "d-flex justify-content-between fw-bold mb-1" }, [
        el("span", { text: r.author || "Reader" }),
        el("span", { text: shortDate(r.created_at) })
      ]),
      el("p", { className: "mb-1" }, [makeStars(r.rating)]),
      el("p", { className: "mb-0", text: r.comment || "" })
    ]));
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

  document.title = book.title + " - Book Details";

  const coverBox = document.getElementById("coverBox");
  coverBox.textContent = "";
  coverBox.appendChild(createCover(book, "L", "object-fit-cover bg-secondary-subtle book-cover-large"));

  document.getElementById("bookTitle").textContent = book.title;
  document.getElementById("bookAuthors").textContent = "by " + book.authors.join(", ");
  document.getElementById("bookGenre").textContent = book.genre || "No genre";

  // Rating chip: stars, average and number of reviews
  const ratingBox = document.getElementById("bookRating");
  ratingBox.textContent = "";
  if (book.rating === null) {
    ratingBox.textContent = "no ratings yet";
  } else {
    const count = book.reviews.length === 1 ? "1 review" : book.reviews.length + " reviews";
    ratingBox.appendChild(makeStars(book.rating));
    ratingBox.appendChild(document.createTextNode(" " + book.rating + " (" + count + ")"));
  }

  document.getElementById("bookDescription").textContent = book.description || "No description yet.";

  // Borrow (or Reserve) and the number of free copies.
  // After borrowing, the whole book is loaded again so the numbers update.
  const buttonBox = document.getElementById("borrowBox");
  buttonBox.textContent = "";
  buttonBox.appendChild(createBorrowButton(book, loadBook, "btn btn-danger px-4"));
  document.getElementById("copiesInfo").textContent =
    book.available_copies + " of " + book.total_copies + " copies available";

  renderReviews(book.reviews);
  return book;
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
async function submitReview(event) {
  event.preventDefault();
  const form = document.getElementById("reviewForm");
  hideBoxMessage("reviewError");
  hideBoxMessage("reviewSuccess");

  // value of the checked radio button, or "" when none is chosen
  const rating = form.elements["rating"].value;
  if (rating === "") {
    showBoxMessage("reviewError", "Please select a rating from 1 to 5.");
    return;
  }

  try {
    await apiPost("/api/books/" + bookId + "/reviews/", {
      rating: parseInt(rating),
      comment: form.elements["comment"].value.trim()
    });
  } catch (err) {
    // e.g. "You have already reviewed this book."
    showBoxMessage("reviewError", err.message);
    return;
  }

  form.reset();
  showBoxMessage("reviewSuccess", "Thank you, your review was saved.");
  loadBook();
}

// First load: the book, then the Open Library block (only once)
async function startPage() {
  const book = await loadBook();
  if (book !== null) {
    loadOpenLibrary(book);
  }
}

// DOMContentLoaded waits until every script (also openlibrary.js) is loaded
document.addEventListener("DOMContentLoaded", function () {
  if (bookId === null || bookId === "") {
    showNotFound("No book was selected. Please choose one in the catalog.");
    return;
  }
  document.getElementById("reviewForm").addEventListener("submit", submitReview);
  startPage();
  setupReviewForm();
});
