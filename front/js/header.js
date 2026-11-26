// Fills the account area of the header (Sign in / Hi, name / Log out)

// Creates a link element with text
function makeLink(text, href, className) {
  const a = document.createElement("a");
  a.textContent = text;
  a.href = href;
  if (className) {
    a.className = className;
  }
  return a;
}

// Asks the API who is logged in and draws the right links.
// /api/me/ also gives the browser the csrftoken cookie.
async function loadHeader() {
  const box = document.getElementById("account");

  let me;
  try {
    me = await apiGet("/api/me/");
  } catch (err) {
    showAlert("Could not check your account. " + err.message);
    return;
  }

  box.textContent = "";

  if (me.logged_in) {
    box.appendChild(makeLink("Hi, " + me.first_name, "profile.html"));

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-outline-primary btn-sm";
    button.textContent = "Log out";
    button.addEventListener("click", logOut);
    box.appendChild(button);
  } else {
    box.appendChild(makeLink("Sign in", "login.html"));
    box.appendChild(makeLink("Create account", "register.html", "btn btn-primary btn-sm"));
  }
}

// Logs out on the server, then reloads the page
async function logOut() {
  try {
    await apiPost("/api/logout/");
    location.reload();
  } catch (err) {
    showAlert(err.message);
  }
}

loadHeader();
