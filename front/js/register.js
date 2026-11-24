// Registration form: client-side checks first, then POST /api/register/

const fieldIds = ["username", "password", "confirmPassword", "birthYear"];

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

// Checks the form and, if everything is fine, creates the account
async function registerUser() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const birthYear = parseInt(document.getElementById("birthYear").value);

  clearErrors();
  let isValid = true;

  if (username.length < 2) {
    showError("username", "Username must have at least 2 characters.");
    isValid = false;
  }

  if (password === "") {
    showError("password", "Please enter a password.");
    isValid = false;
  }

  if (password !== confirmPassword) {
    showError("confirmPassword", "Passwords do not match.");
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

  if (!isValid) {
    return;
  }

  // The server checks the same rules again (and that the name is free)
  try {
    await apiPost("/api/register/", {
      username: username,
      password: password,
      confirm_password: confirmPassword,
      birth_year: birthYear
    });
  } catch (err) {
    showBoxMessage("formError", err.message);
    return;
  }

  // The server already logged the new user in
  location.href = "profile.html";
}
