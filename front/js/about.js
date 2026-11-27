// About page: the "Display settings" buttons.
// The work itself is done by js/theme.js; here we only connect the buttons.
// Each button keeps its value in a data- attribute, read with this.dataset.

const themeButtons = document.querySelectorAll("#display [data-theme-button]");
for (let i = 0; i < themeButtons.length; i++) {
  themeButtons[i].addEventListener("click", function () {
    setTheme(this.dataset.themeButton);
  });
}

const fontButtons = document.querySelectorAll("[data-font-button]");
for (let i = 0; i < fontButtons.length; i++) {
  fontButtons[i].addEventListener("click", function () {
    setFont(this.dataset.fontButton);
  });
}

const sizeButtons = document.querySelectorAll("[data-size-step]");
for (let i = 0; i < sizeButtons.length; i++) {
  sizeButtons[i].addEventListener("click", function () {
    changeSize(parseInt(this.dataset.sizeStep));
  });
}

document.getElementById("resetDisplay").addEventListener("click", resetSettings);
