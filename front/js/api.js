// Shared helpers for talking to the Django JSON API (back/catalog/views.py)

// Returns the value of a cookie, or "" if there is no such cookie
function getCookie(name) {
  const parts = document.cookie.split(";");

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i].trim();
    if (part.startsWith(name + "=")) {
      return decodeURIComponent(part.substring(name.length + 1));
    }
  }

  return "";
}

// Sends a request and returns the parsed JSON.
// Throws an Error with a readable message when something goes wrong.
async function sendRequest(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (err) {
    throw new Error("Network error: the server cannot be reached.");
  }

  // Django can answer with an HTML page (for example the 403 CSRF page)
  let data;
  try {
    data = await response.json();
  } catch (err) {
    const error = new Error("Unexpected server response (status " + response.status + "). Please reload the page.");
    error.status = response.status;
    throw error;
  }

  // Our API sends {"error": "..."} together with a 4xx status
  if (!response.ok) {
    const error = new Error(data.error || "Request failed (status " + response.status + ").");
    error.status = response.status;
    throw error;
  }

  return data;
}

// GET request, returns the JSON data
async function apiGet(url) {
  return sendRequest(url, { method: "GET" });
}

// POST request with a JSON body. The CSRF token is read from the cookie
// right now, because Django changes it after login.
async function apiPost(url, data) {
  return sendRequest(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify(data || {})
  });
}

// Shows a Bootstrap alert in the top right corner.
// type: "primary" for errors, "secondary" for normal messages.
// link (optional): { href: "...", text: "..." }
function showAlert(message, type, link) {
  let area = document.getElementById("alertArea");
  if (area === null) {
    area = document.createElement("div");
    area.id = "alertArea";
    area.className = "alert-area";
    document.body.appendChild(area);
  }

  const alert = document.createElement("div");
  alert.className = "alert alert-" + (type || "primary");
  alert.setAttribute("role", "alert");

  const text = document.createElement("div");
  text.className = "flex-grow-1";
  text.textContent = message;

  if (link) {
    const a = document.createElement("a");
    a.href = link.href;
    a.textContent = link.text;
    a.className = "alert-link ms-1";
    text.appendChild(a);
  }

  const close = document.createElement("button");
  close.type = "button";
  close.className = "btn-close";
  close.setAttribute("aria-label", "Close");
  close.addEventListener("click", function () {
    alert.remove();
  });

  alert.appendChild(text);
  alert.appendChild(close);
  area.appendChild(alert);
}

// Shows a message inside an alert box that already exists on the page
function showBoxMessage(id, message) {
  const box = document.getElementById(id);
  box.textContent = message;
  box.classList.remove("d-none");
}

// Hides an alert box that already exists on the page
function hideBoxMessage(id) {
  const box = document.getElementById(id);
  box.textContent = "";
  box.classList.add("d-none");
}
