// Profile page: the user's loans and reviews from GET /api/me/

// Text for the "Returned" column of a loan
function loanStatus(loan) {
  if (loan.return_date) {
    return "Returned " + loan.return_date;
  }
  // Dates are "YYYY-MM-DD" strings, so they can be compared as text
  const today = new Date().toISOString().slice(0, 10);
  if (loan.due_date < today) {
    return "Overdue";
  }
  return "Not yet";
}

// Creates a table cell with text
function makeCell(text) {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

// Creates a link to the book page
function makeBookLink(bookId, title) {
  const a = document.createElement("a");
  a.href = "book.html?id=" + bookId;
  a.textContent = title;
  return a;
}

// Fills the "My loans" table
function renderLoans(loans) {
  const body = document.getElementById("loanRows");
  body.textContent = "";
  document.getElementById("noLoans").classList.toggle("d-none", loans.length > 0);

  for (let i = 0; i < loans.length; i++) {
    const row = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.appendChild(makeBookLink(loans[i].book_id, loans[i].title));
    row.appendChild(titleCell);
    row.appendChild(makeCell(loans[i].loan_date));
    row.appendChild(makeCell(loans[i].due_date));
    row.appendChild(makeCell(loanStatus(loans[i])));
    body.appendChild(row);
  }
}

// Fills the "My reviews" list, each title links to its book page
function renderReviews(reviews) {
  const list = document.getElementById("reviewList");
  list.textContent = "";
  document.getElementById("noReviews").classList.toggle("d-none", reviews.length > 0);

  for (let i = 0; i < reviews.length; i++) {
    const r = reviews[i];
    const item = document.createElement("li");
    item.className = "review";

    const link = makeBookLink(r.book_id, r.book_title);

    const rating = document.createElement("span");
    rating.className = "text-muted-ink ms-2";
    rating.textContent = r.rating + " / 5";

    const comment = document.createElement("p");
    comment.className = "mb-0";
    comment.textContent = r.comment || "";

    item.appendChild(link);
    item.appendChild(rating);
    item.appendChild(comment);
    list.appendChild(item);
  }
}

// Loads the profile, or asks the visitor to sign in
async function loadProfile() {
  let me;
  try {
    me = await apiGet("/api/me/");
  } catch (err) {
    showAlert("Could not load your profile. " + err.message);
    return;
  }

  if (!me.logged_in) {
    document.getElementById("signedOut").classList.remove("d-none");
    return;
  }

  document.getElementById("profileName").textContent = me.first_name + " " + me.last_name;
  document.getElementById("profileEmail").textContent = me.email;
  renderLoans(me.loans);
  renderReviews(me.reviews);
  document.getElementById("signedIn").classList.remove("d-none");
}

loadProfile();
