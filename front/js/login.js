// Login form: POST /api/login/, then go to the profile

async function loginUser() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  hideBoxMessage("formError");

  if (username === "" || password === "") {
    showBoxMessage("formError", "Please enter your username and password.");
    return;
  }

  try {
    await apiPost("/api/login/", { username: username, password: password });
  } catch (err) {
    // e.g. "Wrong username or password."
    showBoxMessage("formError", err.message);
    return;
  }

  location.href = "profile.html";
}
