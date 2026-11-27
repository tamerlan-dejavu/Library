// "From Open Library" block on the book page.
// The browser asks the public Open Library API directly (no key is needed).

// Shows one line instead of the data (nothing found, or an error)
function showOpenLibraryText(text) {
  document.getElementById("olStatus").textContent = text;
}

// Adds "label | value" to the facts list (Bootstrap grid columns)
function addFact(label, value) {
  const dt = document.createElement("dt");
  dt.className = "col-sm-5 fw-semibold";
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.className = "col-sm-7 mb-1";
  dd.textContent = value;
  document.getElementById("olFacts").appendChild(dt);
  document.getElementById("olFacts").appendChild(dd);
}

// Shows year, editions, rating, up to 6 subjects and the link
function showOpenLibraryData(doc) {
  addFact("First published", doc.first_publish_year || "Unknown");
  addFact("Editions", doc.edition_count || "Unknown");
  if (doc.ratings_average) {
    addFact("Average rating", doc.ratings_average.toFixed(1) + " / 5 (" + doc.ratings_count + " ratings)");
  }
  const subjects = doc.subject || [];
  for (let i = 0; i < subjects.length && i < 6; i++) {
    const badge = document.createElement("span");
    badge.className = "badge subject-badge";
    badge.textContent = subjects[i];
    document.getElementById("olSubjects").appendChild(badge);
  }
  document.getElementById("olLink").href = "https://openlibrary.org" + doc.key;   // "/works/OL...W"
  document.getElementById("olStatus").classList.add("d-none");
  document.getElementById("olData").classList.remove("d-none");
}

// Asks Open Library about this book (title + first author), one request
async function loadOpenLibrary(book) {
  let url = "https://openlibrary.org/search.json?title=" + encodeURIComponent(book.title);
  if (book.authors.length > 0) {
    url = url + "&author=" + encodeURIComponent(book.authors[0]);
  }
  url = url + "&limit=1&fields=key,first_publish_year,edition_count,subject,ratings_average,ratings_count";

  try {
    const response = await fetch(url);
    const data = await response.json();
    if (data.docs.length === 0) {
      showOpenLibraryText("No data found");
    } else {
      showOpenLibraryData(data.docs[0]);
    }
  } catch (err) {
    showOpenLibraryText("Open Library is not available right now. Please try again later.");
  }
}
