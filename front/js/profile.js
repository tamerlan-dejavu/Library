// Profile page: personal data (editable names and phones), My books, My reviews

const MAX_PHONES = 5;
let profile = null;   // the last answer of /api/me/

// Same rules as the server (catalog/views.py)
function isValidName(name) {
  return name.length >= 2 && /^[\p{L} '’-]+$/u.test(name) && /\p{L}/u.test(name);
}
const PHONE_RULE = /^\+?[0-9]{10,15}$/;   // same as the CHECK in schema.sql

// "2026-11-24T08:30:00" -> "2026-11-24"
function shortDate(value) {
  return value ? value.slice(0, 10) : "";
}

// Today as "YYYY-MM-DD" in local time
function todayText() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

// Yellow stars like the reference, or "not rated"
function ratingNode(rating) {
  if (!rating) {
    return el("p", { className: "mb-1", text: "not rated" });
  }
  return el("p", { className: "stars mb-1", role: "img", "aria-label": rating + " out of 5 stars",
                   text: starsText(rating) });
}

// Status of a loan: [text, badge colour]
function loanStatus(loan) {
  if (loan.return_date) {
    return ["Returned", "bg-secondary"];
  }
  if (loan.due_date < todayText()) {
    return ["Overdue", "bg-danger"];
  }
  return ["Borrowed", "bg-dark"];
}

// One card in the style of the reference review cards; the cards sit in a
// .profile-list (Flexbox column with even gaps, see style.css)
function profileCard(children) {
  return el("article", { className: "card card-body bg-secondary-subtle border-0 border-top border-3 border-danger" }, children);
}

// Title (link to the book page) on the left, date on the right
function cardHead(bookId, title, right) {
  return el("div", { className: "review-meta mb-1" }, [
    el("a", { href: "book.html?id=" + bookId, className: "fw-bold link-body-emphasis text-decoration-none", text: title }),
    right
  ]);
}

// ---------- view mode ----------

function renderPersonal() {
  document.getElementById("profileName").textContent = profile.first_name + " " + profile.last_name;
  document.getElementById("profileEmail").textContent = profile.email;
  document.getElementById("profileBirthYear").textContent = profile.birth_year || "—";

  const list = document.getElementById("phoneList");
  list.textContent = "";
  if (profile.phones.length === 0) {
    list.appendChild(el("p", { className: "bg-secondary-subtle p-2 mb-0", text: "No phone number yet" }));
  }
  for (let i = 0; i < profile.phones.length; i++) {
    list.appendChild(el("p", { className: "bg-secondary-subtle p-2 mb-1", text: profile.phones[i] }));
  }
}

// "My books": loans and pending reservations
function renderBooks() {
  const box = document.getElementById("bookRows");
  box.textContent = "";
  let count = 0;

  for (let i = 0; i < profile.loans.length; i++) {
    const loan = profile.loans[i];
    const status = loanStatus(loan);
    const date = loan.return_date ? "Returned " + shortDate(loan.return_date) : "Due " + loan.due_date;
    box.appendChild(profileCard([
      cardHead(loan.book_id, loan.title, el("span", { text: date })),
      ratingNode(loan.rating),
      el("p", { className: "mb-1", text: loan.author || "" }),
      el("p", { className: "mb-0" }, [el("span", { className: "badge " + status[1], text: status[0] })])
    ]));
    count++;
  }
  for (let i = 0; i < profile.reservations.length; i++) {
    const res = profile.reservations[i];
    box.appendChild(profileCard([
      cardHead(res.book_id, res.title, el("span", { text: "Reserved " + shortDate(res.reserved_at) })),
      ratingNode(res.rating),
      el("p", { className: "mb-1", text: res.author || "" }),
      el("p", { className: "mb-0" }, [el("span", { className: "badge bg-warning text-dark", text: "Reserved" })])
    ]));
    count++;
  }
  document.getElementById("noBooks").classList.toggle("d-none", count > 0);
}

// "My reviews": exactly like the reference cards
function renderReviews() {
  const box = document.getElementById("myReviewList");
  box.textContent = "";
  for (let i = 0; i < profile.reviews.length; i++) {
    const r = profile.reviews[i];
    box.appendChild(profileCard([
      cardHead(r.book_id, r.book_title, el("span", { text: shortDate(r.created_at) })),
      ratingNode(r.rating),
      el("p", { className: "mb-1", text: r.author || "" }),
      el("p", { className: "mb-0", text: r.comment || "" })
    ]));
  }
  document.getElementById("noReviews").classList.toggle("d-none", profile.reviews.length > 0);
}

function renderAll() {
  renderPersonal();
  renderBooks();
  renderReviews();
}

// ---------- edit mode ----------

// One phone input with a "Remove" button
function addPhoneRow(value) {
  const rows = document.getElementById("phoneRows");
  const number = rows.children.length + 1;
  const input = el("input", { type: "tel", className: "form-control phone-input",
                              "aria-label": "Phone " + number, placeholder: "+77011234567",
                              "aria-describedby": "phonesError" });
  input.value = value || "";
  const remove = el("button", { type: "button", className: "btn btn-outline-secondary",
                                "aria-label": "Remove phone " + number, text: "Remove" });
  const row = el("div", { className: "d-flex gap-2 mb-2" }, [input, remove]);
  remove.addEventListener("click", function () {
    row.remove();
    updateAddButton();
  });
  rows.appendChild(row);
  updateAddButton();
}

// "Add phone" is hidden when there are already 5 numbers
function updateAddButton() {
  const count = document.getElementById("phoneRows").children.length;
  document.getElementById("addPhone").classList.toggle("d-none", count >= MAX_PHONES);
}

function setEditMode(on) {
  document.getElementById("nameEdit").classList.toggle("d-none", !on);
  document.getElementById("phoneEdit").classList.toggle("d-none", !on);
  document.getElementById("phoneList").classList.toggle("d-none", on);
  document.getElementById("editButton").classList.toggle("d-none", on);
  document.getElementById("editButtons").classList.toggle("d-none", !on);
  clearFormErrors();

  if (on) {
    document.getElementById("firstName").value = profile.first_name;
    document.getElementById("lastName").value = profile.last_name;
    document.getElementById("phoneRows").textContent = "";
    for (let i = 0; i < profile.phones.length; i++) {
      addPhoneRow(profile.phones[i]);
    }
    document.getElementById("firstName").focus();
  }
}

function showFieldError(id, message) {
  document.getElementById(id).classList.add("is-invalid");
  document.getElementById(id + "Error").textContent = message;
}

function clearFormErrors() {
  for (const id of ["firstName", "lastName"]) {
    document.getElementById(id).classList.remove("is-invalid");
    document.getElementById(id + "Error").textContent = "";
  }
  document.getElementById("phonesError").textContent = "";
  hideBoxMessage("profileError");
  hideBoxMessage("profileSuccess");
}

// Checks the form like the server does, then sends PATCH /api/me/
async function saveProfile(event) {
  event.preventDefault();
  clearFormErrors();

  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const phones = [];
  const inputs = document.querySelectorAll(".phone-input");
  for (let i = 0; i < inputs.length; i++) {
    const phone = inputs[i].value.replace(/ /g, "").trim();
    if (phone !== "") {
      phones.push(phone);
    }
  }

  let ok = true;
  if (!isValidName(firstName)) {
    showFieldError("firstName", "At least 2 letters (spaces, - and ' are allowed).");
    ok = false;
  }
  if (!isValidName(lastName)) {
    showFieldError("lastName", "At least 2 letters (spaces, - and ' are allowed).");
    ok = false;
  }
  const badPhone = phones.find(function (p) { return !PHONE_RULE.test(p); });
  if (badPhone) {
    document.getElementById("phonesError").textContent = badPhone + ": use + and 10-15 digits, e.g. +77011234567.";
    ok = false;
  } else if (new Set(phones).size !== phones.length) {
    document.getElementById("phonesError").textContent = "The same phone number is entered twice.";
    ok = false;
  }
  if (!ok) {
    return;
  }

  try {
    profile = await apiPatch("/api/me/", { first_name: firstName, last_name: lastName, phones: phones });
  } catch (err) {
    if (err.field === "first_name") {
      showFieldError("firstName", err.message);
    } else if (err.field === "last_name") {
      showFieldError("lastName", err.message);
    } else if (err.field === "phones") {
      document.getElementById("phonesError").textContent = err.message;
    } else {
      showBoxMessage("profileError", err.message);
    }
    return;
  }

  setEditMode(false);
  renderAll();
  showBoxMessage("profileSuccess", "Your profile was saved.");
}

// ---------- start ----------

async function loadProfile() {
  let me;
  try {
    me = await apiGet("/api/me/");
  } catch (err) {
    showAlert("Could not load your profile. " + err.message);
    return;
  }
  // Without an account there is no profile: go to the sign-in page
  if (!me.logged_in) {
    location.replace("login.html");
    return;
  }
  profile = me;
  renderAll();
  document.getElementById("profileArea").classList.remove("d-none");
}

document.getElementById("editButton").addEventListener("click", function () { setEditMode(true); });
document.getElementById("cancelButton").addEventListener("click", function () { setEditMode(false); });
document.getElementById("addPhone").addEventListener("click", function () { addPhoneRow(""); });
document.getElementById("profileForm").addEventListener("submit", saveProfile);
loadProfile();
