// "From Open Library" card on the book page.
// The browser calls the public Open Library API directly (it allows this
// with the header Access-Control-Allow-Origin: *). No key is needed.

const OPEN_LIBRARY = "https://openlibrary.org";

// Builds the search URL from the title and the first author
function openLibraryUrl(book) {
  let url = OPEN_LIBRARY + "/search.json?title=" + encodeURIComponent(book.title);
  if (book.authors.length > 0) {
    url = url + "&author=" + encodeURIComponent(book.authors[0]);
  }
  return url + "&limit=1&fields=key,first_publish_year,edition_count,subject,ratings_average,ratings_count";
}

// Replaces the loading text with a short message
function showOpenLibraryMessage(text) {
  const status = document.getElementById("olStatus");
  status.textContent = text;
}

// Adds a "label: value" line to the Open Library facts
function addOpenLibraryFact(list, label, value) {
  const dt = document.createElement("dt");
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.textContent = value;
  list.appendChild(dt);
  list.appendChild(dd);
}

// Loads the Open Library data for a book and fills the card
async function loadOpenLibrary(book) {
  let data;
  try {
    const response = await fetch(openLibraryUrl(book));
    if (!response.ok) {
      throw new Error("status " + response.status);
    }
    data = await response.json();
  } catch (err) {
    showOpenLibraryMessage("Open Library is not available right now. Please try again later.");
    return;
  }

  if (data.docs.length === 0) {
    showOpenLibraryMessage("No data found");
    return;
  }

  const doc = data.docs[0];

  const facts = document.getElementById("olFacts");
  facts.textContent = "";
  addOpenLibraryFact(facts, "First published", doc.first_publish_year || "Unknown");
  addOpenLibraryFact(facts, "Editions", doc.edition_count || "Unknown");
  if (doc.ratings_average) {
    addOpenLibraryFact(facts, "Average rating",
      doc.ratings_average.toFixed(1) + " / 5 (" + doc.ratings_count + " ratings)");
  }

  // Up to 6 subjects as small badges
  const subjects = document.getElementById("olSubjects");
  subjects.textContent = "";
  const list = (doc.subject || []).slice(0, 6);
  for (let i = 0; i < list.length; i++) {
    const badge = document.createElement("span");
    badge.className = "badge subject-badge";
    badge.textContent = list[i];
    subjects.appendChild(badge);
  }

  // doc.key looks like "/works/OL893414W"
  document.getElementById("olLink").href = OPEN_LIBRARY + doc.key;

  document.getElementById("olStatus").classList.add("d-none");
  document.getElementById("olData").classList.remove("d-none");
}
