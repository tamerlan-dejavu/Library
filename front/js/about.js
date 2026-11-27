// About page: the "Display settings" buttons (theme, font, text size).
// The work itself is done by js/theme.js; here we only connect the buttons.

function connectDisplayButtons() {
  const themeButtons = document.querySelectorAll("#display [data-theme-button]");
  for (let i = 0; i < themeButtons.length; i++) {
    themeButtons[i].addEventListener("click", function () {
      setTheme(themeButtons[i].dataset.themeButton);
    });
  }

  const fontButtons = document.querySelectorAll("[data-font-button]");
  for (let i = 0; i < fontButtons.length; i++) {
    fontButtons[i].addEventListener("click", function () {
      setFont(fontButtons[i].dataset.fontButton);
    });
  }

  const sizeButtons = document.querySelectorAll("[data-size-step]");
  for (let i = 0; i < sizeButtons.length; i++) {
    sizeButtons[i].addEventListener("click", function () {
      changeSize(parseInt(sizeButtons[i].dataset.sizeStep));
    });
  }

  document.getElementById("resetDisplay").addEventListener("click", resetDisplay);
}

connectDisplayButtons();
