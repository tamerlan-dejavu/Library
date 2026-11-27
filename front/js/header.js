// Header of every page. The HTML of the header is written in each page;
// this file only:
// 1) marks the active menu item (from <body data-page="...">),
// 2) shows "Create account | Sign in" or "Switch account | Log out",
// 3) connects the Lt / Dt theme buttons.

// Marks the menu link of the current page as active
function markActiveMenu() {
  const page = document.body.dataset.page;
  const links = document.querySelectorAll(".site-menu-links .nav-link");
  for (let i = 0; i < links.length; i++) {
    if (links[i].dataset.menu === page) {
      links[i].classList.add("active");
      links[i].setAttribute("aria-current", "page");
    }
  }
}

// Shows the links for a guest or for a logged-in user
function showAccountLinks(loggedIn) {
  const guestLinks = document.querySelectorAll(".guest-link");
  for (let i = 0; i < guestLinks.length; i++) {
    guestLinks[i].classList.toggle("d-none", loggedIn);
  }
  const userLinks = document.querySelectorAll(".user-link");
  for (let i = 0; i < userLinks.length; i++) {
    userLinks[i].classList.toggle("d-none", !loggedIn);
  }
  // Without an account the Profile item leads to the sign-in page
  if (!loggedIn) {
    document.getElementById("profileMenuLink").href = "login.html";
  }
}

// Asks the API who is logged in. /api/me/ also gives the browser the
// csrftoken cookie that our POST requests need.
async function loadAccount() {
  try {
    const me = await apiRequest("/api/me/", "GET");
    showAccountLinks(me.logged_in);
  } catch (err) {
    showAccountLinks(false);
  }
}

// Logs out, then opens another page (Switch account) or reloads this one
async function logOut(nextPage) {
  try {
    await apiRequest("/api/logout/", "POST");
  } catch (err) {
    alert(err.message);
    return;
  }
  if (nextPage === "") {
    location.reload();
  } else {
    location.href = nextPage;
  }
}

markActiveMenu();
loadAccount();

document.getElementById("lightTheme").addEventListener("click", function () {
  setTheme("paper");
});
document.getElementById("darkTheme").addEventListener("click", function () {
  setTheme("night");
});
document.getElementById("switchAccount").addEventListener("click", function () {
  logOut("login.html");
});
document.getElementById("logOut").addEventListener("click", function () {
  logOut("");
});
