// Profile page: personal data (names and phones can be changed),
// "My books" (loans and reservations) and "My reviews"

let profile = null;   // the last answer of /api/me/

// Stars for a rating, e.g. 4 -> "★★★★☆"
function starsText(rating) {
  let stars = "";
  for (let i = 1; i <= 5; i++) {
    stars = stars + (i <= rating ? "★" : "☆");
  }
  return stars;
}

// Name, e-mail, birth year and phones (view mode)
function showProfile() {
  document.getElementById("profileName").textContent = profile.first_name + " " + profile.last_name;
  document.getElementById("profileEmail").textContent = profile.email;
  document.getElementById("profileBirthYear").textContent = profile.birth_year || "—";

  let phones = profile.phones;
  if (phones.length === 0) {
    phones = ["No phone number yet"];
  }
  const list = document.getElementById("phoneList");
  list.textContent = "";
  for (let i = 0; i < phones.length; i++) {
    const line = document.getElementById("phoneTemplate").content.firstElementChild.cloneNode(true);
    line.textContent = phones[i];
    list.appendChild(line);
  }
}

// One card from <template id="profileCardTemplate">
function makeCard(bookId, title, date, rating, author) {
  const card = document.getElementById("profileCardTemplate").content.firstElementChild.cloneNode(true);
  card.querySelector(".card-book").href = "book.html?id=" + bookId;
  card.querySelector(".card-book").textContent = title;
  card.querySelector(".card-date").textContent = date;
  card.querySelector(".card-author").textContent = author || "";
  const stars = card.querySelector(".card-rating");
  stars.textContent = "not rated";
  if (rating) {
    stars.textContent = starsText(rating);
    stars.className = "stars mb-1 card-rating";
    stars.setAttribute("role", "img");
    stars.setAttribute("aria-label", rating + " out of 5 stars");
  }
  return card;
}

// Adds the coloured status label (Borrowed, Returned, Overdue, Reserved)
function setStatus(card, text, colours) {
  const label = card.querySelector(".card-status");
  label.textContent = text;
  label.className = "badge card-status " + colours;
}

// "My books": loans and waiting reservations
function loadBooks() {
  const box = document.getElementById("bookRows");
  const today = new Date().toISOString().slice(0, 10);
  box.textContent = "";
  for (let i = 0; i < profile.loans.length; i++) {
    const loan = profile.loans[i];
    let date = "Due " + loan.due_date;
    let status = "Borrowed";
    let colours = "bg-dark";
    if (loan.return_date) {
      date = "Returned " + loan.return_date;
      status = "Returned";
      colours = "bg-secondary";
    } else if (loan.due_date < today) {
      status = "Overdue";
      colours = "bg-danger";
    }
    const card = makeCard(loan.book_id, loan.title, date, loan.rating, loan.author);
    setStatus(card, status, colours);
    box.appendChild(card);
  }
  for (let i = 0; i < profile.reservations.length; i++) {
    const res = profile.reservations[i];
    const card = makeCard(res.book_id, res.title, "Reserved " + res.reserved_at.slice(0, 10), res.rating, res.author);
    setStatus(card, "Reserved", "bg-warning text-dark");
    box.appendChild(card);
  }
  const count = profile.loans.length + profile.reservations.length;
  document.getElementById("noBooks").classList.toggle("d-none", count > 0);
}

// "My reviews"
function loadReviews() {
  const box = document.getElementById("myReviewList");
  box.textContent = "";
  for (let i = 0; i < profile.reviews.length; i++) {
    const r = profile.reviews[i];
    const card = makeCard(r.book_id, r.book_title, r.created_at.slice(0, 10), r.rating, r.author);
    card.querySelector(".card-comment").textContent = r.comment || "";
    box.appendChild(card);
  }
  document.getElementById("noReviews").classList.toggle("d-none", profile.reviews.length > 0);
}

// One phone input with a "Remove" button, from <template id="phoneEditTemplate">
function addPhoneRow(value) {
  const row = document.getElementById("phoneEditTemplate").content.firstElementChild.cloneNode(true);
  row.querySelector("input").value = value;
  row.querySelector(".remove-phone").addEventListener("click", function () {
    row.remove();
    document.getElementById("addPhone").classList.remove("d-none");
  });
  document.getElementById("phoneRows").appendChild(row);
  // at most 5 numbers
  document.getElementById("addPhone").classList.toggle("d-none", document.querySelectorAll(".phone-row").length >= 5);
}

// Shows or hides the inputs and the buttons of the edit mode
function setEditMode(editing) {
  document.getElementById("nameEdit").classList.toggle("d-none", !editing);
  document.getElementById("phoneEdit").classList.toggle("d-none", !editing);
  document.getElementById("phoneList").classList.toggle("d-none", editing);
  document.getElementById("editButton").classList.toggle("d-none", editing);
  document.getElementById("editButtons").classList.toggle("d-none", !editing);
  document.getElementById("firstName").classList.remove("is-invalid");
  document.getElementById("lastName").classList.remove("is-invalid");
  document.getElementById("phonesError").textContent = "";
  document.getElementById("profileError").classList.add("d-none");
  document.getElementById("profileSuccess").classList.add("d-none");
}

// "Change profile": names and phones become inputs
function startEditing() {
  setEditMode(true);
  document.getElementById("firstName").value = profile.first_name;
  document.getElementById("lastName").value = profile.last_name;
  document.getElementById("phoneRows").textContent = "";
  for (let i = 0; i < profile.phones.length; i++) {
    addPhoneRow(profile.phones[i]);
  }
  document.getElementById("firstName").focus();
}

// "Cancel": back to the view mode without saving
function cancelEditing() {
  setEditMode(false);
}

// Marks a field as invalid and writes the message under it
function showFieldError(id, message) {
  if (id === "phones") {
    document.getElementById("phonesError").textContent = message;
    return;
  }
  document.getElementById(id).classList.add("is-invalid");
  document.getElementById(id + "Error").textContent = message;
}

// Reads the phone inputs; empty rows are skipped, spaces removed
function readPhones() {
  const phones = [];
  const inputs = document.querySelectorAll(".phone-input");
  for (let i = 0; i < inputs.length; i++) {
    const phone = inputs[i].value.split(" ").join("");
    if (phone !== "") {
      phones.push(phone);
    }
  }
  return phones;
}

// Checks names and phones like the server does. Returns true when all is fine.
function checkProfileForm(firstName, lastName, phones) {
  let isValid = true;
  if (firstName.length < 2 || /[0-9]/.test(firstName)) {
    showFieldError("firstName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }
  if (lastName.length < 2 || /[0-9]/.test(lastName)) {
    showFieldError("lastName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }
  for (let i = 0; i < phones.length; i++) {
    if (!/^\+?[0-9]{10,15}$/.test(phones[i])) {   // the same rule as the CHECK in schema.sql
      showFieldError("phones", phones[i] + ": use + and 10-15 digits, e.g. +77011234567.");
      isValid = false;
    } else if (phones.indexOf(phones[i]) !== i) {
      showFieldError("phones", "The same phone number is entered twice.");
      isValid = false;
    }
  }
  return isValid;
}

// "Save": checks the form, then sends PATCH /api/me/
async function saveProfile(event) {
  event.preventDefault();
  setEditMode(true);   // clears old messages
  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const phones = readPhones();
  if (!checkProfileForm(firstName, lastName, phones)) {
    return;
  }
  try {
    profile = await apiRequest("/api/me/", "PATCH", { first_name: firstName, last_name: lastName, phones: phones });
  } catch (err) {
    if (err.field === "first_name") {
      showFieldError("firstName", err.message);
    } else if (err.field === "last_name") {
      showFieldError("lastName", err.message);
    } else if (err.field === "phones") {
      showFieldError("phones", err.message);
    } else {
      document.getElementById("profileError").textContent = err.message;
      document.getElementById("profileError").classList.remove("d-none");
    }
    return;
  }
  setEditMode(false);
  showProfile();
  document.getElementById("profileSuccess").textContent = "Your profile was saved.";
  document.getElementById("profileSuccess").classList.remove("d-none");
}

// Start: without an account there is no profile, so go to the sign-in page
async function startPage() {
  try {
    profile = await apiRequest("/api/me/", "GET");
  } catch (err) {
    document.getElementById("profileError").textContent = "Could not load your profile. " + err.message;
    return;
  }
  if (!profile.logged_in) {
    location.replace("login.html");
    return;
  }
  showProfile();
  loadBooks();
  loadReviews();
  document.getElementById("profileArea").classList.remove("d-none");
}

document.getElementById("editButton").addEventListener("click", startEditing);
document.getElementById("cancelButton").addEventListener("click", cancelEditing);
document.getElementById("addPhone").addEventListener("click", function () {
  addPhoneRow("");
});
document.getElementById("profileForm").addEventListener("submit", saveProfile);
startPage();
