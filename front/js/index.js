// Home page: shows up to 4 bestsellers from the API

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
  const books = data.books.slice(0, 4);
  for (let i = 0; i < books.length; i++) {
    grid.appendChild(createBookCard(books[i], loadBestsellers));
  }
}

loadBestsellers();
