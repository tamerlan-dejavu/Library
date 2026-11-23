function updateHeader() {
  const link = document.getElementById("accountLink");

  if (link === null) {
    return;
  }

  const data = localStorage.getItem("user");

  if (data === null) {
    link.textContent = "Create account";
    link.href = "register.html";
  } else {
    const user = JSON.parse(data);
    link.textContent = "Hi, " + user.username;
    link.href = "profile-demo.html";
  }
}

updateHeader();
