"use strict";
(() => {
  const lengthInput = document.getElementById("generator-length");
  const output = document.getElementById("generated-password");
  const status = document.getElementById("generator-status");
  const copy = document.getElementById("copy-password");
  const use = document.getElementById("use-generated");
  const pools = { uppercase: "ABCDEFGHIJKLMNOPQRSTUVWXYZ", lowercase: "abcdefghijklmnopqrstuvwxyz", numbers: "0123456789", symbols: "!@#$%^&*()-_=+[]{}:,.?" };
  lengthInput.addEventListener("input", () => { document.getElementById("length-value").value = lengthInput.value; });
  window.PSC.bindVisibility(document.getElementById("generator-toggle"), output);
  function randomIndex(size) {
    const limit = Math.floor(0x100000000 / size) * size;
    const values = new Uint32Array(1);
    do { crypto.getRandomValues(values); } while (values[0] >= limit);
    return values[0] % size;
  }
  document.getElementById("generate-button").addEventListener("click", () => {
    if (!globalThis.crypto?.getRandomValues) { status.textContent = "Secure randomness isn't available in this browser. Use a modern browser over HTTPS or localhost."; return; }
    let selected = Object.entries(pools).filter(([key]) => document.getElementById(`gen-${key}`).checked).map(([, value]) => value);
    if (!selected.length) { status.textContent = "Choose at least one character type to generate a password."; return; }
    if (document.getElementById("exclude-similar").checked) selected = selected.map(pool => pool.replace(/[Il1O0]/g, ""));
    const pool = selected.join("");
    const length = Number(lengthInput.value);
    // Rejection sampling makes every string equally likely, conditioned on all selected types being present.
    let characters;
    do { characters = Array.from({ length }, () => pool[randomIndex(pool.length)]); }
    while (!selected.every(group => characters.some(character => group.includes(character))));
    output.value = characters.join("");
    copy.disabled = false;
    use.disabled = false;
    status.textContent = `Fresh ${length}-character password generated. Copy it into your password manager.`;
  });
  copy.addEventListener("click", async () => {
    if (!output.value) return;
    try { await navigator.clipboard.writeText(output.value); status.textContent = "Copied. Save it in your password manager; your clipboard may retain it until replaced."; }
    catch (_) { status.textContent = "Clipboard access is unavailable. Show the password, select it, and copy manually."; }
  });
  use.addEventListener("click", () => {
    const input = document.getElementById("password-input");
    if (input.disabled) { status.textContent = "The checker is still loading. Try again in a moment."; return; }
    input.value = output.value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    document.getElementById("checker").scrollIntoView({ behavior: "smooth", block: "start" });
    input.focus({ preventScroll: true });
  });
  window.addEventListener("pagehide", () => { output.value = ""; });
  window.addEventListener("pageshow", () => { copy.disabled = !output.value; use.disabled = !output.value; });
})();
