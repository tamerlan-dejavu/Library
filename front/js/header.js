// Header and footer of every page (the one place where they are defined).
// The page has <div id="siteHeader"></div> and <div id="siteFooter"></div>,
// and <body data-page="home|catalog|profile|about|..."> marks the active menu item.

const MENU = [
  { page: "home", text: "Home", href: "index.html" },
  { page: "catalog", text: "Catalog", href: "catalog.html" },
  { page: "profile", text: "Profile", href: "profile.html" },
  { page: "about", text: "About", href: "about.html" }
];

// Logo image as a link to the home page. The bars are dark in every theme,
// so data-logo="on-dark" makes theme.js always use the light mark here.
function makeLogo() {
  return el("a", { href: "index.html", "aria-label": "Book Catalog home" }, [
    el("img", { src: "assets/logo-paper.png", "data-logo": "on-dark", alt: "Book Catalog logo",
                height: "40", width: "40" })
  ]);
}

// Dark top bar: logo on the left, account links on the right (Flexbox in style.css)
function makeTopBar() {
  return el("header", { className: "bg-dark py-2" }, [
    el("div", { className: "container-fluid px-4 site-top-inner" }, [
      makeLogo(),
      el("div", { id: "account", className: "site-account" })
    ])
  ]);
}

// "Lt | Dt": two small buttons that switch between light and dark theme
function makeThemeSwitch() {
  const light = el("button", { type: "button", className: "btn btn-outline-light btn-sm",
                               "data-theme-button": "paper", "aria-label": "Light theme", text: "Lt" });
  const dark = el("button", { type: "button", className: "btn btn-outline-light btn-sm",
                              "data-theme-button": "night", "aria-label": "Dark theme", text: "Dt" });
  light.addEventListener("click", function () { setTheme("paper"); });
  dark.addEventListener("click", function () { setTheme("night"); });
  return el("div", { className: "btn-group", role: "group", "aria-label": "Theme" }, [light, dark]);
}

// Burgundy menu bar (sticky): menu, theme switch and search
function makeMenuBar() {
  const current = document.body.dataset.page;
  const items = [];
  for (let i = 0; i < MENU.length; i++) {
    const link = el("a", { className: "nav-link", href: MENU[i].href, text: MENU[i].text });
    if (MENU[i].page === current) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
    if (MENU[i].page === "profile") {
      link.id = "profileMenuLink";
    }
    items.push(el("li", { className: "nav-item" }, [link]));
  }

  const search = el("form", { action: "catalog.html", method: "get", role: "search" }, [
    el("input", { type: "search", name: "q", placeholder: "Find your next favorite book...",
                  className: "form-control form-control-sm", "aria-label": "Search" })
  ]);

  // navbar-nav / nav-link give the Bootstrap link colours; the layout
  // (row, or a column on phones) comes from .site-menu-* in style.css
  return el("div", { className: "sticky-top" }, [
    el("nav", { className: "navbar navbar-expand navbar-dark bg-brand", "aria-label": "Main" }, [
      el("div", { className: "container-fluid px-4 site-menu-inner" }, [
        el("ul", { className: "navbar-nav site-menu-links" }, items),
        el("div", { className: "site-tools" }, [makeThemeSwitch(), search])
      ])
    ])
  ]);
}

// Dark footer: logo, short text, links, author and data credit
function makeFooter() {
  return el("footer", { className: "bg-dark text-white mt-4" }, [
    el("div", { className: "container-fluid px-4 py-4" }, [
      el("div", { className: "site-footer-inner" }, [
        el("div", { className: "site-footer-about" }, [
          makeLogo(),
          el("p", { className: "mt-2 mb-0", text: "Discover, borrow and read your favorite books online." }),
          el("p", { className: "mt-4 mb-0", text: "Created by Bauyrzhan Tamerlan" })
        ]),
        el("div", { className: "site-footer-links" }, [
          el("p", {}, [
            el("a", { href: "about.html#privacy", className: "text-white me-2", text: "Privacy Policy" }),
            el("a", { href: "about.html#faq", className: "text-white", text: "Help & FAQ" })
          ]),
          el("p", { className: "mb-0" }, [
            el("a", { href: "about.html#contact", className: "text-white", text: "Contact us" })
          ]),
          el("p", { className: "mt-3 mb-0 small text-white-50" }, [
            document.createTextNode("Book data and covers: "),
            el("a", { href: "https://openlibrary.org", rel: "noopener", className: "text-white-50", text: "Open Library" })
          ])
        ])
      ])
    ])
  ]);
}

// Account links: "Create account / Sign in" or "Switch account / Log out"
function fillAccount(me) {
  const box = document.getElementById("account");
  box.textContent = "";

  if (me.logged_in) {
    const switchLink = el("button", { type: "button", className: "btn btn-link link-light p-0", text: "Switch account" });
    const logoutLink = el("button", { type: "button", className: "btn btn-link link-light p-0", text: "Log out" });
    switchLink.addEventListener("click", function () { logOut("login.html"); });
    logoutLink.addEventListener("click", function () { logOut(null); });
    box.appendChild(switchLink);
    box.appendChild(logoutLink);
  } else {
    box.appendChild(el("a", { href: "register.html", className: "btn btn-outline-light btn-sm", text: "Create account" }));
    box.appendChild(el("a", { href: "login.html", className: "text-white text-decoration-none", text: "Sign in" }));
    // Without an account the Profile item leads to the sign-in page
    document.getElementById("profileMenuLink").href = "login.html";
  }
}

// Logs out, then reloads the page or opens another one (Switch account)
async function logOut(nextPage) {
  try {
    await apiPost("/api/logout/");
  } catch (err) {
    showAlert(err.message);
    return;
  }
  if (nextPage) {
    location.href = nextPage;
  } else {
    location.reload();
  }
}

// Draws header and footer, then asks the API who is logged in.
// /api/me/ also gives the browser the csrftoken cookie.
async function loadHeader() {
  document.getElementById("siteHeader").appendChild(makeTopBar());
  document.getElementById("siteHeader").appendChild(makeMenuBar());
  document.getElementById("siteFooter").appendChild(makeFooter());
  applyDisplay();   // mark the pressed Lt/Dt button

  try {
    fillAccount(await apiGet("/api/me/"));
  } catch (err) {
    showAlert("Could not check your account. " + err.message);
  }
}

loadHeader();
