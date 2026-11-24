// Theme presets. Loaded in <head> so the saved theme applies before drawing.
// The colors themselves live in css/style.css ([data-theme="..."]).

// Puts the theme name on <html data-theme="..."> and marks the active button
function applyTheme(name) {
  document.documentElement.dataset.theme = name;

  const buttons = document.querySelectorAll("[data-theme-button]");
  for (let i = 0; i < buttons.length; i++) {
    const isActive = buttons[i].dataset.themeButton === name;
    buttons[i].setAttribute("aria-pressed", isActive ? "true" : "false");
  }
}

// Called by the switcher buttons: apply and remember the choice
function setTheme(name) {
  try {
    localStorage.setItem("theme", name);
  } catch (err) {
    // Storage can be blocked (private mode); the theme still applies
  }
  applyTheme(name);
}

// "Reset to default" button
function resetTheme() {
  try {
    localStorage.removeItem("theme");
  } catch (err) {
    // ignore, see setTheme
  }
  applyTheme("paper");
}

// Returns the saved theme name, or "paper" if nothing is saved
function savedTheme() {
  try {
    return localStorage.getItem("theme") || "paper";
  } catch (err) {
    return "paper";
  }
}

applyTheme(savedTheme());

// The switcher buttons exist only after the page is parsed
document.addEventListener("DOMContentLoaded", function () {
  applyTheme(savedTheme());
});
