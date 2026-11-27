// Registration form: checks in the browser first, then POST /api/register/

const fieldIds = ["firstName", "lastName", "email", "birthYear", "password", "password2"];

// Marks a field as invalid and writes the message under it
function showError(id, message) {
  document.getElementById(id).classList.add("is-invalid");
  document.getElementById(id + "Error").textContent = message;
}

// Removes all error marks and messages
function clearErrors() {
  for (let i = 0; i < fieldIds.length; i++) {
    document.getElementById(fieldIds[i]).classList.remove("is-invalid");
    document.getElementById(fieldIds[i] + "Error").textContent = "";
  }
  document.getElementById("formError").classList.add("d-none");
}

// A name: at least 2 characters and no digits (the server checks the rest)
function isGoodName(name) {
  if (name.length < 2) {
    return false;
  }
  for (let i = 0; i < name.length; i++) {
    if (name[i] >= "0" && name[i] <= "9") {
      return false;
    }
  }
  return true;
}

// Checks the form; if everything is fine, creates the account
function registerUser() {
  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const birthYear = parseInt(document.getElementById("birthYear").value);
  const password = document.getElementById("password").value;
  const password2 = document.getElementById("password2").value;

  clearErrors();
  let isValid = true;

  if (!isGoodName(firstName)) {
    showError("firstName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }

  if (!isGoodName(lastName)) {
    showError("lastName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }

  // something@something.something, without spaces
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError("email", "Please enter a valid email address.");
    isValid = false;
  }

  const age = new Date().getFullYear() - birthYear;
  if (isNaN(birthYear)) {
    showError("birthYear", "Please enter your birth year.");
    isValid = false;
  } else if (birthYear < 1900) {
    showError("birthYear", "Please enter a real birth year.");
    isValid = false;
  } else if (age <= 18) {
    showError("birthYear", "You must be older than 18.");
    isValid = false;
  }

  if (password === "") {
    showError("password", "Please enter a password.");
    isValid = false;
  }

  if (password !== password2) {
    showError("password2", "Passwords do not match.");
    isValid = false;
  }

  if (isValid) {
    sendRegistration(firstName, lastName, email, birthYear, password, password2);
  }
}

// Sends the form to the server; it checks the same rules again
async function sendRegistration(firstName, lastName, email, birthYear, password, password2) {
  try {
    await apiRequest("/api/register/", "POST", {
      first_name: firstName, last_name: lastName, email: email,
      birth_year: birthYear, password: password, password2: password2
    });
  } catch (err) {
    // Show the message under the field it belongs to
    if (err.field === "first_name") {
      showError("firstName", err.message);
    } else if (err.field === "last_name") {
      showError("lastName", err.message);
    } else if (err.field === "email") {
      showError("email", err.message);
    } else if (err.field === "birth_year") {
      showError("birthYear", err.message);
    } else if (err.field === "password" || err.field === "password2") {
      showError(err.field, err.message);
    } else {
      document.getElementById("formError").textContent = err.message;
      document.getElementById("formError").classList.remove("d-none");
    }
    return;
  }
  // The server has already logged the new user in
  location.href = "profile.html";
}

document.getElementById("registerForm").addEventListener("submit", function (event) {
  event.preventDefault();   // stay on the page; we send the data with fetch
  registerUser();
});
