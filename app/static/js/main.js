"use strict";
(() => {
  let theme = "light";
  try { theme = localStorage.getItem("psc-theme") === "dark" ? "dark" : "light"; } catch (_) { /* Storage may be disabled. */ }
  document.documentElement.dataset.theme = theme;
  window.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("theme-toggle");
    function renderThemeButton() {
      const dark = document.documentElement.dataset.theme === "dark";
      button.setAttribute("aria-label", `Switch to ${dark ? "light" : "dark"} mode`);
      button.innerHTML = `<i class="bi bi-${dark ? "sun" : "moon"}" aria-hidden="true"></i>`;
    }
    renderThemeButton();
    button.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("psc-theme", next); } catch (_) { /* Preference persistence is optional. */ }
      renderThemeButton();
      document.dispatchEvent(new Event("themechange"));
    });
    const menu = document.getElementById("menu-toggle");
    menu.addEventListener("click", () => {
      const open = menu.getAttribute("aria-expanded") !== "true";
      menu.setAttribute("aria-expanded", String(open));
      menu.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      document.getElementById("nav-links").classList.toggle("open", open);
    });
    const adminToggle = document.getElementById("admin-password-toggle");
    if (adminToggle) bindVisibility(adminToggle, document.getElementById("admin-password"));
  });
  function bindVisibility(button, input) {
    button.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-pressed", String(show));
      button.setAttribute("aria-label", `${show ? "Hide" : "Show"} ${input.id === "generated-password" ? "generated password" : "password"}`);
      button.innerHTML = `<i class="bi bi-${show ? "eye-slash" : "eye"}" aria-hidden="true"></i>`;
    });
  }
  window.PSC = { bindVisibility };
})();
