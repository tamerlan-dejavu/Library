// Registration form: client-side checks first, then POST /api/register/

const fieldIds = ["firstName", "lastName", "email", "birthYear", "password", "password2"];

// Server field name -> id of the input on this page
const serverFields = {
  first_name: "firstName",
  last_name: "lastName",
  email: "email",
  birth_year: "birthYear",
  password: "password",
  password2: "password2"
};

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
  hideBoxMessage("formError");
}

// Name rule (same as the server): at least 2 characters, letters of any
// alphabet, and also space, hyphen and apostrophe. \p{L} = any letter.
function isValidName(name) {
  return name.length >= 2 && /^[\p{L} '’-]+$/u.test(name) && /\p{L}/u.test(name);
}

// Simple e-mail check: something@something.something, no spaces
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Checks the form and, if everything is fine, creates the account
async function registerUser() {
  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const birthYear = parseInt(document.getElementById("birthYear").value);
  const password = document.getElementById("password").value;
  const password2 = document.getElementById("password2").value;

  clearErrors();
  let isValid = true;

  if (!isValidName(firstName)) {
    showError("firstName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }

  if (!isValidName(lastName)) {
    showError("lastName", "At least 2 letters (spaces, - and ' are allowed).");
    isValid = false;
  }

  if (!isValidEmail(email)) {
    showError("email", "Please enter a valid email address.");
    isValid = false;
  }

  const currentYear = new Date().getFullYear();
  const age = currentYear - birthYear;

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

  if (!isValid) {
    return;
  }

  // The server checks the same rules again (and that the email is free)
  try {
    await apiPost("/api/register/", {
      first_name: firstName,
      last_name: lastName,
      email: email,
      birth_year: birthYear,
      password: password,
      password2: password2
    });
  } catch (err) {
    // Show the message under the field it belongs to, if we know it
    if (err.field && serverFields[err.field]) {
      showError(serverFields[err.field], err.message);
    } else {
      showBoxMessage("formError", err.message);
    }
    return;
  }

  // The server already logged the new user in
  location.href = "profile.html";
}
