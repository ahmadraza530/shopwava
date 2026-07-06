function applyTheme(theme) {
  if (theme === "light") {
    document.body.classList.add("light-theme");
  } else {
    document.body.classList.remove("light-theme");
  }
}

function toggleTheme() {
  const isLight = document.body.classList.contains("light-theme");
  const newTheme = isLight ? "dark" : "light";
  applyTheme(newTheme);
  localStorage.setItem("theme", newTheme);
  updateToggleLabel(newTheme);
}

function updateToggleLabel(theme) {
  const label = document.getElementById("theme-label");
  if (label) {
    label.textContent = theme === "light" ? "Dark" : "Light";
  }
}

const savedTheme = localStorage.getItem("theme") || "dark";
applyTheme(savedTheme);
document.addEventListener("DOMContentLoaded", function() {
  updateToggleLabel(savedTheme);
});