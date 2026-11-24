// Book card and Borrow button, shared by index, catalog and book pages

const PLACEHOLDER_COVER = "assets/book-placeholder.svg";

// Turns the average rating into text, e.g. "4.5 / 5" or "No ratings yet"
function ratingText(rating) {
  if (rating === null) {
    return "No ratings yet";
  }
  return rating + " / 5";
}

// Open Library covers come in sizes S, M and L ("...-L.jpg").
// Cards use the medium one, the book page keeps the large one.
function coverUrl(book, size) {
  if (!book.cover_url) {
    return null;
  }
  return book.cover_url.replace("-L.jpg", "-" + size + ".jpg");
}

// Called when a cover fails: show the placeholder at once (so the alt text
// never appears), then try the real cover once more after 2 seconds
function handleCoverError(img, url) {
  img.onerror = null;           // the placeholder can never call us again
  img.src = PLACEHOLDER_COVER;

  setTimeout(function () {
    // Load the cover again in a hidden Image; swap it in only if it works
    const retry = new Image();
    retry.referrerPolicy = "no-referrer";
    retry.onload = function () {
      img.src = url;
    };
    retry.src = url;
  }, 2000);
}

// Creates the cover <img>. size: "M" for cards, "L" for the book page.
function createCover(book, size) {
  const img = document.createElement("img");
  img.className = "book-cover";
  img.alt = "Cover of " + book.title;
  img.loading = "lazy";              // load only when it scrolls into view
  img.decoding = "async";            // decode without blocking the page
  img.referrerPolicy = "no-referrer";

  const url = coverUrl(book, size || "L");
  if (url === null) {
    img.src = PLACEHOLDER_COVER;
    return img;
  }

  // The handler is set BEFORE src, so even a very fast failure is caught
  img.onerror = function () {
    handleCoverError(img, url);
  };
  img.src = url;
  return img;
}

// Creates the Borrow / Reserve button. afterBorrow runs after success.
function createBorrowButton(book, afterBorrow) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "btn btn-primary btn-sm";
  button.textContent = book.available_copies > 0 ? "Borrow" : "Reserve";
  button.addEventListener("click", function () {
    borrowBook(book.id, button, afterBorrow);
  });
  return button;
}

// Sends the borrow request and shows the result in an alert
async function borrowBook(bookId, button, afterBorrow) {
  button.disabled = true;
  try {
    const data = await apiPost("/api/books/" + bookId + "/borrow/");
    showAlert(data.message, "secondary");
    if (afterBorrow) {
      afterBorrow();
    }
  } catch (err) {
    if (err.status === 401) {
      showAlert("Sign in first.", "primary", { href: "login.html", text: "Sign in" });
    } else {
      showAlert(err.message);
    }
  }
  button.disabled = false;
}

// Builds one book card: cover, badge, title, authors, genre, rating, button
function createBookCard(book, afterBorrow) {
  const link = "book.html?id=" + book.id;

  const card = document.createElement("article");
  card.className = "book-card";

  const coverLink = document.createElement("a");
  coverLink.href = link;
  coverLink.appendChild(createCover(book, "M"));
  card.appendChild(coverLink);

  const body = document.createElement("div");
  body.className = "book-card-body";

  if (book.is_bestseller) {
    const badge = document.createElement("span");
    badge.className = "badge bg-primary";
    badge.textContent = "Bestseller";
    body.appendChild(badge);
  }

  const title = document.createElement("h3");
  title.className = "book-title";
  const titleLink = document.createElement("a");
  titleLink.href = link;
  titleLink.textContent = book.title;
  title.appendChild(titleLink);
  body.appendChild(title);

  const authors = document.createElement("p");
  authors.className = "mb-0";
  authors.textContent = book.authors.join(", ");
  body.appendChild(authors);

  const meta = document.createElement("p");
  meta.className = "book-meta mb-2";
  meta.textContent = (book.genre || "No genre") + " · " + ratingText(book.rating);
  body.appendChild(meta);

  body.appendChild(createBorrowButton(book, afterBorrow));
  card.appendChild(body);
  return card;
}
