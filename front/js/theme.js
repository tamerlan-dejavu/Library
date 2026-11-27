// Display settings: theme, text font and text size, saved in localStorage.
// Loaded in <head> on every page, so the saved choice applies before drawing.
// Themes: "paper" (light), "night" (dark, Bootstrap data-bs-theme="dark"),
// "contrast" (black on white).

const SIZES = [14, 16, 18, 20];

// Reads a saved value; localStorage can be blocked (private mode)
function readSetting(name, defaultValue) {
  try {
    const value = localStorage.getItem(name);
    if (value === null) {
      return defaultValue;
    }
    return value;
  } catch (err) {
    return defaultValue;
  }
}

// Saves a value, or removes it when value is null
function saveSetting(name, value) {
  try {
    if (value === null) {
      localStorage.removeItem(name);
    } else {
      localStorage.setItem(name, value);
    }
  } catch (err) {
    // ignore: the setting still works on this page
  }
}

// Puts the saved settings on <html> and updates buttons and logos
function applySettings() {
  let theme = readSetting("theme", "paper");
  const font = readSetting("font", "sans");
  let size = readSetting("size", "16");
  const root = document.documentElement;
  // unknown saved values fall back to the defaults
  if (theme !== "night" && theme !== "contrast") {
    theme = "paper";
  }
  if (SIZES.indexOf(parseInt(size)) === -1) {
    size = "16";
  }

  root.dataset.theme = theme;
  if (theme === "night") {
    root.dataset.bsTheme = "dark";
  } else {
    root.dataset.bsTheme = "light";
  }
  if (font === "serif") {
    root.style.setProperty("--bs-body-font-family", 'Georgia, "Times New Roman", serif');
  } else {
    root.style.removeProperty("--bs-body-font-family");
  }
  root.style.fontSize = size + "px";   // Bootstrap uses rem, so all text scales

  updateLogos(theme);
  updateButtons(theme, font, size);
}

// Logos: <img data-logo="on-dark"> sits on a dark bar and always uses the
// light mark; <img data-logo="auto"> follows the theme
function updateLogos(theme) {
  const logos = document.querySelectorAll("img[data-logo]");
  for (let i = 0; i < logos.length; i++) {
    if (logos[i].dataset.logo === "on-dark" || theme === "night") {
      logos[i].src = "assets/logo-paper.png";
    } else {
      logos[i].src = "assets/logo-ink.png";
    }
  }
}

// Marks the pressed theme and font buttons, shows the text size
function updateButtons(theme, font, size) {
  const themeButtons = document.querySelectorAll("[data-theme-button]");
  for (let i = 0; i < themeButtons.length; i++) {
    themeButtons[i].setAttribute("aria-pressed", String(themeButtons[i].dataset.themeButton === theme));
  }
  const fontButtons = document.querySelectorAll("[data-font-button]");
  for (let i = 0; i < fontButtons.length; i++) {
    fontButtons[i].setAttribute("aria-pressed", String(fontButtons[i].dataset.fontButton === font));
  }
  const sizeLabels = document.querySelectorAll("[data-size-label]");
  for (let i = 0; i < sizeLabels.length; i++) {
    sizeLabels[i].textContent = size + " px";
  }
}

function setTheme(name) {
  saveSetting("theme", name);
  applySettings();
}

function setFont(name) {
  saveSetting("font", name);
  applySettings();
}

// step: -1 (A-), +1 (A+) or 0 (A = back to 16 px)
function changeSize(step) {
  let index = SIZES.indexOf(parseInt(readSetting("size", "16")));
  if (index === -1 || step === 0) {
    index = 1;               // 16 px
  } else {
    index = index + step;
  }
  if (index < 0) {
    index = 0;
  }
  if (index > SIZES.length - 1) {
    index = SIZES.length - 1;
  }
  saveSetting("size", String(SIZES[index]));
  applySettings();
}

// "Reset to default": light theme, sans font, 16 px
function resetSettings() {
  saveSetting("theme", null);
  saveSetting("font", null);
  saveSetting("size", null);
  applySettings();
}

applySettings();
// Buttons and logos exist only after the page is parsed
document.addEventListener("DOMContentLoaded", applySettings);
