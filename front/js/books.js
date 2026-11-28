// Shared by Home, Catalog and Book pages: messages, covers, book cards, Borrow.
// Each of these pages defines its own function refreshPage(), which loads
// the books again after a successful Borrow.

const PLACEHOLDER = "assets/book-placeholder.svg";

// Shows a message in the top right corner (#alertArea, from <template id="messageTemplate">).
// isError: red box; otherwise grey. linkText/linkHref: an optional link.
function showMessage(text, isError, linkText, linkHref) {
  const box = document.getElementById("messageTemplate").content.firstElementChild.cloneNode(true);
  if (isError) {
    box.classList.add("alert-danger");
  } else {
    box.classList.add("alert-secondary");
  }
  box.querySelector(".message-text").textContent = text;
  if (linkText) {
    const link = box.querySelector(".message-link");
    link.textContent = linkText;
    link.href = linkHref;
    link.classList.remove("d-none");
  }
  box.querySelector(".btn-close").addEventListener("click", function () {
    box.remove();
  });
  document.getElementById("alertArea").appendChild(box);
}

// Puts the cover into an <img>. No cover -> the placeholder at once.
// If the picture cannot be loaded, the placeholder is shown (only once).
// size "M" (cards) or "L" (book page) for Open Library pictures.
function setCover(img, book, size) {
  img.alt = book.title + " cover";
  if (!book.cover_url) {
    img.src = PLACEHOLDER;
    return;
  }
  img.addEventListener("error", function () {
    img.src = PLACEHOLDER;
  }, { once: true });
  if (book.cover_url.startsWith("http")) {
    img.src = book.cover_url.replace("-L.jpg", "-" + size + ".jpg");
  } else {
    img.src = book.cover_url;   // our own copy, e.g. "covers/12.jpg"
  }
}

// Makes one book card from <template id="bookCardTemplate">
function makeBookCard(book, showBadge) {
  const card = document.getElementById("bookCardTemplate").content.firstElementChild.cloneNode(true);
  const link = "book.html?id=" + book.id;

  card.querySelector(".cover-link").href = link;
  setCover(card.querySelector("img"), book, "M");
  if (showBadge && book.is_bestseller) {
    card.querySelector(".book-card-badge").classList.remove("d-none");
  }
  // "Tamer's pick" (only the catalog card template has this badge)
  const pick = card.querySelector(".book-card-pick");
  if (pick !== null && book.is_recommended) {
    pick.classList.remove("d-none");
  }
  card.querySelector(".title-link").href = link;
  card.querySelector(".title-link").textContent = book.title;
  card.querySelector(".book-card-author").textContent = book.authors.join(", ");

  const button = card.querySelector(".book-card-action");
  setBorrowButton(button, book);
  return card;
}

// Text and click of the Borrow / Reserve button
function setBorrowButton(button, book) {
  if (book.available_copies > 0) {
    button.textContent = "Borrow";
  } else {
    button.textContent = "Reserve";
  }
  button.addEventListener("click", function () {
    borrowBook(book.id, button);
  });
}

// Sends the borrow request and shows the answer
async function borrowBook(bookId, button) {
  button.disabled = true;
  try {
    const data = await apiRequest("/api/books/" + bookId + "/borrow/", "POST");
    showMessage(data.message, false);
    refreshPage();
  } catch (err) {
    if (err.status === 401) {
      showMessage("Sign in first.", true, "Sign in", "login.html");
    } else {
      showMessage(err.message, true);
    }
  }
  button.disabled = false;
}
