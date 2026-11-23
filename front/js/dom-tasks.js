// Task 2. Collects all tags on the page and prints them to the console.
function showAllTags() {
  const tags = document.getElementsByTagName("*");

  for (let i = 0; i < tags.length; i++) {
    console.log(i + 1, tags[i].tagName, tags[i].innerHTML);
  }

  document.getElementById("tagsResult").textContent =
    "Found " + tags.length + " tags. Open the console (F12) to see them.";
}

// Task 3. Fully replaces the content of the block using innerHTML.
function replaceBlock() {
  const block = document.getElementById("replaceBlock");

  block.innerHTML =
    "<h5 class='text-danger'>New content!</h5>" +
    "<p>This block was fully replaced with JavaScript.</p>" +
    "<ul class='mb-0'>" +
    "<li>Old text was removed</li>" +
    "<li>New HTML was added with innerHTML</li>" +
    "</ul>";
}

// Task 4. Changes the font of the text.
function changeFont() {
  document.getElementById("styleText").style.fontFamily = "Georgia, serif";
  document.getElementById("styleText").style.fontSize = "22px";
}

// Task 4. Changes the color of the text.
function changeColor() {
  document.getElementById("styleText").style.color = "#7a2e2e";
}

// Task 4. Switches the picture to another one by changing src.
function changeImage() {
  const image = document.getElementById("styleImage");

  if (image.src.includes("book1.png")) {
    image.src = "assets/book2.png";
  } else {
    image.src = "assets/book1.png";
  }
}

// Task 4. Returns the text and the picture to the start state.
function resetStyles() {
  const text = document.getElementById("styleText");
  text.style.fontFamily = "";
  text.style.fontSize = "";
  text.style.color = "";
  document.getElementById("styleImage").src = "assets/book1.png";
}
