// One helper for all requests to our Django API (back/catalog/views.py).
// method: "GET", "POST" or "PATCH"; data: the object to send (or nothing).
// Returns the answer as an object, or throws an Error with a clear message.
async function apiRequest(url, method, data) {
  const options = { method: method, headers: {} };

  if (method !== "GET") {
    // Django wants the CSRF token from the "csrftoken" cookie in a header.
    // We read it now, because it changes after login.
    let token = "";
    const cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
      if (cookies[i].startsWith("csrftoken=")) {
        token = cookies[i].substring("csrftoken=".length);
      }
    }
    options.headers["X-CSRFToken"] = token;
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data || {});
  }

  let response;
  try {
    response = await fetch(url, options);
  } catch (err) {
    throw new Error("Network error: the server cannot be reached.");
  }

  let result;
  try {
    result = await response.json();
  } catch (err) {
    // e.g. Django's HTML page for a CSRF error
    result = { error: "Unexpected server response (status " + response.status + "). Please reload the page." };
  }

  if (!response.ok) {
    const problem = new Error(result.error || "Request failed (status " + response.status + ").");
    problem.status = response.status;
    problem.field = result.field;   // the form field the error belongs to
    throw problem;
  }
  return result;
}
