// Book cover and book card, shared by Home, Catalog and Book pages

const PLACEHOLDER_COVER = "assets/book-placeholder.svg";

// Average rating as stars, e.g. 3.6 -> "★★★★☆" (rounded to whole stars)
function starsText(rating) {
  const full = Math.round(rating || 0);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

// Open Library covers come in sizes S, M and L ("...-L.jpg").
// Cards use the medium one, the book page the large one.
// Our own copies ("covers/12.jpg") are used as they are.
function coverUrl(book, size) {
  if (!book.cover_url) {
    return null;
  }
  if (!book.cover_url.startsWith("http")) {
    return book.cover_url;
  }
  return book.cover_url.replace("-L.jpg", "-" + size + ".jpg");
}

// Called when a cover fails: show the placeholder at once, then try the
// real cover once more after 2 seconds and use it only if it loads
function handleCoverError(img, url) {
  img.onerror = null;           // the placeholder can never call us again
  img.src = PLACEHOLDER_COVER;

  setTimeout(function () {
    const retry = new Image();
    retry.referrerPolicy = "no-referrer";
    retry.onload = function () {
      img.src = url;
    };
    retry.src = url;
  }, 2000);
}

// Creates the cover <img>. size: "M" for cards, "L" for the book page.
// className sets the look (card picture or big picture).
function createCover(book, size, className) {
  const img = el("img", { alt: book.title + " cover", className: className, loading: "lazy", decoding: "async" });
  img.referrerPolicy = "no-referrer";

  const url = coverUrl(book, size);
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

// Borrow / Reserve button. afterBorrow runs after success.
function createBorrowButton(book, afterBorrow, className) {
  const button = el("button", {
    type: "button", className: className || "btn btn-danger",
    text: book.available_copies > 0 ? "Borrow" : "Reserve"
  });
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
      showAlert("Sign in first.", "danger", { href: "login.html", text: "Sign in" });
    } else {
      showAlert(err.message);
    }
  }
  button.disabled = false;
}

// One book card, a direct item of the .book-grid (CSS Grid).
// The card itself is a Flexbox column (see .book-card in style.css):
// cover, optional "Bestseller" badge, title, author, Borrow button at the bottom.
function createBookCard(book, options) {
  const settings = options || {};
  const link = "book.html?id=" + book.id;

  const coverLink = el("a", { href: link, tabindex: "-1", "aria-hidden": "true" }, [
    createCover(book, "M", "object-fit-cover book-card-cover")
  ]);
  let cover = coverLink;
  if (settings.showBadge && book.is_bestseller) {
    cover = el("div", { className: "position-relative" }, [
      coverLink,
      el("span", { className: "badge bg-danger book-card-badge", text: "Bestseller" })
    ]);
  }

  return el("article", { className: "book-card" }, [
    cover,
    el("h3", { className: "book-card-title" }, [el("a", { href: link, text: book.title })]),
    el("p", { className: "book-card-author", text: book.authors.join(", ") }),
    createBorrowButton(book, settings.afterBorrow, "btn btn-danger book-card-action")
  ]);
}
