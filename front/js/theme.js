// Display settings: theme, body font and text size.
// Loaded in <head> on every page, so the saved choice applies before drawing.
// Saved in localStorage: "theme" (paper | night | contrast),
// "font" (sans | serif) and "size" (14 | 16 | 18 | 20).
// The dark theme uses Bootstrap's own colour mode: <html data-bs-theme="dark">.

const THEMES = ["paper", "night", "contrast"];
const SIZES = [14, 16, 18, 20];
const FONTS = {
  sans: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  serif: 'Georgia, "Times New Roman", serif'
};

// Reads a saved value; storage can be blocked (private mode)
function readSetting(key, fallback) {
  try {
    return localStorage.getItem(key) || fallback;
  } catch (err) {
    return fallback;
  }
}

// Saves a value, or removes it when value is null
function writeSetting(key, value) {
  try {
    if (value === null) {
      localStorage.removeItem(key);
    } else {
      localStorage.setItem(key, value);
    }
  } catch (err) {
    // ignore: the setting still applies on this page
  }
}

// The current settings, with defaults
function currentTheme() {
  const theme = readSetting("theme", "paper");
  return THEMES.includes(theme) ? theme : "paper";
}

function currentFont() {
  return readSetting("font", "sans") === "serif" ? "serif" : "sans";
}

function currentSize() {
  const size = parseInt(readSetting("size", "16"));
  return SIZES.includes(size) ? size : 16;
}

// Marks the pressed button of a group (aria-pressed="true")
function markPressed(selector, dataKey, value) {
  const buttons = document.querySelectorAll(selector);
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute("aria-pressed", buttons[i].dataset[dataKey] === value ? "true" : "false");
  }
}

// Puts all settings on <html> and updates the buttons on the page
function applyDisplay() {
  const root = document.documentElement;
  const theme = currentTheme();
  root.dataset.theme = theme;
  root.dataset.bsTheme = theme === "night" ? "dark" : "light";
  root.style.setProperty("--bs-body-font-family", FONTS[currentFont()]);
  // Bootstrap sizes everything in rem, so the whole page scales with this
  root.style.fontSize = currentSize() + "px";

  markPressed("[data-theme-button]", "themeButton", theme);
  markPressed("[data-font-button]", "fontButton", currentFont());
  const sizeLabels = document.querySelectorAll("[data-size-label]");
  for (let i = 0; i < sizeLabels.length; i++) {
    sizeLabels[i].textContent = currentSize() + " px";
  }
}

function setTheme(name) {
  writeSetting("theme", name);
  applyDisplay();
}

function setFont(name) {
  writeSetting("font", name);
  applyDisplay();
}

// step: -1 (A-), +1 (A+) or 0 (A = back to 16 px)
function changeSize(step) {
  let index = step === 0 ? 1 : SIZES.indexOf(currentSize()) + step;
  index = Math.max(0, Math.min(SIZES.length - 1, index));
  writeSetting("size", String(SIZES[index]));
  applyDisplay();
}

// "Reset to default": light theme, sans font, 16 px
function resetDisplay() {
  writeSetting("theme", null);
  writeSetting("font", null);
  writeSetting("size", null);
  applyDisplay();
}

applyDisplay();

// Buttons exist only after the page is parsed
document.addEventListener("DOMContentLoaded", applyDisplay);
