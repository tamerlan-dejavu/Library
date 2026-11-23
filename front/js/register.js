const fieldIds = ["username", "password", "confirmPassword", "birthYear", "photo", "about"];

function showError(id, message) {
  document.getElementById(id).classList.add("is-invalid");
  document.getElementById(id + "Error").textContent = message;
}

function clearErrors() {
  for (let i = 0; i < fieldIds.length; i++) {
    document.getElementById(fieldIds[i]).classList.remove("is-invalid");
    document.getElementById(fieldIds[i] + "Error").textContent = "";
  }
}

function countWords(text) {
  const oneLine = text.split("\n").join(" ");
  const parts = oneLine.split(" ");
  let count = 0;

  for (let i = 0; i < parts.length; i++) {
    if (parts[i] !== "") {
      count = count + 1;
    }
  }

  return count;
}

function updateWordCounter() {
  const words = countWords(document.getElementById("about").value);
  document.getElementById("wordCounter").textContent = words + " / 30 words";
}

function showPhotoPreview() {
  const photo = document.getElementById("photo");
  const preview = document.getElementById("photoPreview");

  if (photo.files.length === 0) {
    preview.classList.add("d-none");
  } else {
    preview.src = URL.createObjectURL(photo.files[0]);
    preview.classList.remove("d-none");
  }
}

function registerUser() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const birthYear = parseInt(document.getElementById("birthYear").value);
  const photo = document.getElementById("photo");
  const about = document.getElementById("about").value.trim();

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

  if (photo.files.length === 0) {
    showError("photo", "Please choose a photo.");
    isValid = false;
  }

  const words = countWords(about);
  if (words < 30) {
    showError("about", "Write at least 30 words about yourself (now: " + words + ").");
    isValid = false;
  }

  if (isValid) {
    const user = {
      username: username,
      birthYear: birthYear,
      about: about
    };

    localStorage.setItem("user", JSON.stringify(user));
    updateHeader();
    alert("Registration was successful!");

    document.getElementById("registerForm").reset();
    showPhotoPreview();
    updateWordCounter();
  }
}

function showProfile() {
  const message = document.getElementById("profileMessage");
  const box = document.getElementById("profileBox");
  const data = localStorage.getItem("user");

  if (data === null) {
    box.classList.add("d-none");
    message.textContent = "No saved user data was found.";
    return;
  }

  const user = JSON.parse(data);
  const age = new Date().getFullYear() - user.birthYear;

  message.textContent = "";
  document.getElementById("profileAvatar").textContent = user.username.charAt(0).toUpperCase();
  document.getElementById("profileName").textContent = user.username;
  document.getElementById("profileAge").textContent = age;
  document.getElementById("profileAbout").textContent = user.about;
  box.classList.remove("d-none");
}

function clearProfile() {
  localStorage.removeItem("user");
  updateHeader();
  document.getElementById("profileBox").classList.add("d-none");
  document.getElementById("profileMessage").textContent = "Profile was cleared.";
}
