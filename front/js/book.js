// Book page: book.html?id=N - details, Borrow, reviews and the review form

const bookId = new URLSearchParams(location.search).get("id");

// Stars for a rating, e.g. 3.6 -> "★★★★☆" (rounded to whole stars)
function starsText(rating) {
  const full = Math.round(rating);
  let stars = "";
  for (let i = 1; i <= 5; i++) {
    if (i <= full) {
      stars = stars + "★";
    } else {
      stars = stars + "☆";
    }
  }
  return stars;
}

// Shows a friendly message instead of the book
function showNotFound(text) {
  document.getElementById("bookArea").classList.add("d-none");
  document.getElementById("notFound").textContent = text;
  document.getElementById("notFound").classList.remove("d-none");
}

// Title, authors, genre, rating, description, cover and copies
function showBook(book) {
  document.title = book.title + " - Book Details";
  setCover(document.getElementById("bookCover"), book, "L");
  document.getElementById("bookTitle").textContent = book.title;
  document.getElementById("bookAuthors").textContent = "by " + book.authors.join(", ");
  document.getElementById("bookGenre").textContent = book.genre || "No genre";
  document.getElementById("bookDescription").textContent = book.description || "No description yet.";

  const rating = document.getElementById("bookRating");
  if (book.rating === null) {
    rating.textContent = "no ratings yet";
  } else {
    rating.textContent = starsText(book.rating) + " " + book.rating + " (" + book.reviews.length + " reviews)";
  }
  document.getElementById("copiesInfo").textContent =
    book.available_copies + " of " + book.total_copies + " copies available";

  // A new button each time, so an old click handler is not kept
  const box = document.getElementById("borrowBox");
  box.textContent = "";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "btn btn-danger px-4";
  setBorrowButton(button, book);
  box.appendChild(button);
}

// Reviews (newest first), each from <template id="reviewTemplate">
function showReviews(reviews) {
  const list = document.getElementById("reviewList");
  list.textContent = "";
  if (reviews.length === 0) {
    list.textContent = "No reviews yet. Be the first to write one.";
  }
  for (let i = 0; i < reviews.length; i++) {
    const card = document.getElementById("reviewTemplate").content.firstElementChild.cloneNode(true);
    const stars = card.querySelector(".review-stars");
    card.querySelector(".review-author").textContent = reviews[i].author || "Reader";
    card.querySelector(".review-date").textContent = (reviews[i].created_at || "").slice(0, 10);
    stars.textContent = starsText(reviews[i].rating);
    stars.setAttribute("aria-label", reviews[i].rating + " out of 5 stars");
    card.querySelector(".review-text").textContent = reviews[i].comment || "";
    list.appendChild(card);
  }
}

// Loads the book; returns it, or null when it could not be loaded
async function loadBook() {
  try {
    const book = await apiRequest("/api/books/" + bookId + "/", "GET");
    showBook(book);
    showReviews(book.reviews);
    return book;
  } catch (err) {
    if (err.status === 404) {
      showNotFound("Sorry, we could not find this book.");
    } else {
      showMessage("Could not load the book. " + err.message, true);
    }
    return null;
  }
}

// The review form is only for logged-in users
async function setupReviewForm() {
  try {
    const me = await apiRequest("/api/me/", "GET");
    document.getElementById("reviewForm").classList.toggle("d-none", !me.logged_in);
    document.getElementById("signInToReview").classList.toggle("d-none", me.logged_in);
  } catch (err) {
    showMessage("Could not check your account. " + err.message, true);
  }
}

// Sends the review, then loads the book again to show it
async function sendReview(event) {
  event.preventDefault();
  const form = document.getElementById("reviewForm");
  const rating = form.elements["rating"].value;   // "" when nothing is chosen
  document.getElementById("reviewError").classList.add("d-none");
  document.getElementById("reviewSuccess").classList.add("d-none");

  try {
    if (rating === "") {
      throw new Error("Please select a rating from 1 to 5.");
    }
    await apiRequest("/api/books/" + bookId + "/reviews/", "POST",
      { rating: parseInt(rating), comment: document.getElementById("comment").value.trim() });
  } catch (err) {
    document.getElementById("reviewError").textContent = err.message;   // e.g. "already reviewed"
    document.getElementById("reviewError").classList.remove("d-none");
    return;
  }
  form.reset();
  document.getElementById("reviewSuccess").textContent = "Thank you, your review was saved.";
  document.getElementById("reviewSuccess").classList.remove("d-none");
  loadBook();
}

// After Borrow: load the book again, so the copies line updates
function refreshPage() {
  loadBook();
}

// DOMContentLoaded waits until every script (also openlibrary.js) is loaded
document.addEventListener("DOMContentLoaded", async function () {
  if (!bookId) {
    showNotFound("No book was selected. Please choose one in the catalog.");
    return;
  }
  document.getElementById("reviewForm").addEventListener("submit", sendReview);
  setupReviewForm();
  const book = await loadBook();
  if (book !== null) {
    loadOpenLibrary(book);   // only once, not after every Borrow
  }
});
