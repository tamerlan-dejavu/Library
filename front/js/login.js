// Login form: POST /api/login/ with email and password, then go to the profile

async function loginUser() {
  const email = document.getElementById("email").value.trim().toLowerCase();
  const password = document.getElementById("password").value;

  hideBoxMessage("formError");

  if (email === "" || password === "") {
    showBoxMessage("formError", "Please enter your email and password.");
    return;
  }

  try {
    await apiPost("/api/login/", { email: email, password: password });
  } catch (err) {
    // e.g. "Invalid email or password."
    showBoxMessage("formError", err.message);
    return;
  }

  location.href = "profile.html";
}
