async function loadUsers() {
  const message = document.getElementById("usersMessage");
  const list = document.getElementById("usersList");

  list.innerHTML = "";
  message.innerHTML = "<span class='spinner-border spinner-border-sm me-2'></span>Loading users...";

  try {
    const response = await fetch("https://jsonplaceholder.typicode.com/users");

    if (!response.ok) {
      throw new Error("Users could not be loaded");
    }

    const users = await response.json();

    for (let i = 0; i < users.length; i++) {
      const card = document.createElement("div");
      card.className = "col-12 col-md-6 col-lg-4";
      card.innerHTML =
        "<div class='card h-100 border-0 shadow-sm hover-lift'>" +
          "<div class='card-body d-flex align-items-center gap-3'>" +
            "<span class='avatar'>" + users[i].name.charAt(0) + "</span>" +
            "<div class='text-truncate'>" +
              "<h5 class='card-title mb-0'>" + users[i].name + "</h5>" +
              "<div class='text-secondary'>@" + users[i].username + "</div>" +
              "<a href='mailto:" + users[i].email + "' class='small'>" + users[i].email + "</a>" +
            "</div>" +
          "</div>" +
        "</div>";
      list.appendChild(card);
    }

    message.textContent = "Loaded " + users.length + " users.";
  } catch (error) {
    message.textContent = "Error: users could not be loaded. Check your internet connection.";
  }
}
