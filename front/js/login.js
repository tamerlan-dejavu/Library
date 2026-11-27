// Login form: POST /api/login/ with email and password, then go to the profile

// Shows a message in the red box under the form
function showLoginError(message) {
  document.getElementById("formError").textContent = message;
  document.getElementById("formError").classList.remove("d-none");
}

async function loginUser() {
  const email = document.getElementById("email").value.trim().toLowerCase();
  const password = document.getElementById("password").value;

  document.getElementById("formError").classList.add("d-none");
  if (email === "" || password === "") {
    showLoginError("Please enter your email and password.");
    return;
  }

  try {
    await apiRequest("/api/login/", "POST", { email: email, password: password });
  } catch (err) {
    showLoginError(err.message);   // e.g. "Invalid email or password."
    return;
  }
  location.href = "profile.html";
}

document.getElementById("loginForm").addEventListener("submit", function (event) {
  event.preventDefault();   // stay on the page; we send the data with fetch
  loginUser();
});
