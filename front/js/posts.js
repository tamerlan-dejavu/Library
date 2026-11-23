let currentPost = null;

function formatNumber(number) {
  return String(number).padStart(3, "0");
}

function showPost(post) {
  const number = formatNumber(post.id);

  document.getElementById("postResult").innerHTML =
    "<div class='card border-0 shadow-sm'>" +
      "<div class='card-body p-4'>" +
        "<span class='badge text-bg-danger mb-2'>Post #" + post.id + "</span>" +
        "<h5 class='card-title'>" + number + "</h5>" +
        "<p class='card-text mb-0'>" + number + "</p>" +
      "</div>" +
    "</div>";
}

function showMessage(text, type) {
  const box = document.getElementById("postMessage");
  box.className = "alert alert-" + type + " mt-3 mb-0";
  box.textContent = text;
}

async function findPost() {
  const text = document.getElementById("postId").value.trim();
  document.getElementById("postResult").innerHTML = "";
  currentPost = null;

  if (text === "") {
    showMessage("Error: please enter a post ID.", "danger");
    return;
  }

  const id = Number(text);

  if (isNaN(id) || id < 1 || id > 100) {
    showMessage("Error: ID must be a number from 1 to 100.", "danger");
    return;
  }

  showMessage("Loading post...", "info");

  try {
    const response = await fetch("https://jsonplaceholder.typicode.com/posts/" + id);

    if (response.status === 404) {
      throw new Error("Post not found");
    }

    if (!response.ok) {
      throw new Error("Post could not be loaded");
    }

    const post = await response.json();
    currentPost = post;
    showPost(post);
    showMessage("Post was loaded.", "success");
  } catch (error) {
    if (error.message === "Post not found" || error.message === "Post could not be loaded") {
      showMessage("Error: " + error.message + ".", "danger");
    } else {
      showMessage("Error: request failed. Check your internet connection.", "danger");
    }
  }
}

function savePost() {
  if (currentPost === null) {
    showMessage("Error: find a post first, then save it.", "danger");
    return;
  }

  localStorage.setItem("savedPost", JSON.stringify(currentPost));
  showMessage("Post " + currentPost.id + " was saved.", "success");
}

function showSavedPost() {
  const data = localStorage.getItem("savedPost");

  if (data === null) {
    showMessage("No saved post was found.", "warning");
    document.getElementById("postResult").innerHTML = "";
    return;
  }

  const post = JSON.parse(data);
  currentPost = post;
  showPost(post);
  showMessage("This is your saved post.", "info");
}
