"use strict";
(() => {
  const input = document.getElementById("password-input");
  const saveButton = document.getElementById("save-analysis");
  const saveStatus = document.getElementById("save-status");
  const names = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"];
  const colors = ["#f16f7e", "#f39a61", "#e6b44d", "#50b7c6", "#43d6ac"];
  let rules;
  let result;
  let revision = 0;

  function analyze(password) {
    const characters = [...password];
    const length = characters.length;
    const lower = password.toLowerCase();
    const substitutions = { "@": "a", "0": "o", "4": "a", "3": "e", "1": "i", "5": "s", "7": "t", "$": "s", "!": "i" };
    const normalized = lower.replace(/[@043157$!]/g, value => substitutions[value]);
    const criteria = {
      uppercase: /[A-Z]/.test(password), lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password), symbol: /[^A-Za-z0-9\s]/u.test(password)
    };
    const common = rules.common_passwords.includes(lower);
    const dictionary = rules.dictionary_words.some(word => lower.includes(word) || normalized.includes(word));
    const sequential = rules.sequences.some(sequence => {
      for (let index = 0; index <= sequence.length - 4; index++) {
        const block = sequence.slice(index, index + 4);
        if (lower.includes(block) || lower.includes([...block].reverse().join(""))) return true;
      }
      return false;
    });
    const repeated = /(.)\1{2,}/u.test(password);
    const repeatedPattern = /^(.{1,4})\1{2,}$/u.test(password);
    const lowDiversity = length >= 8 && new Set([...lower]).size / length < 0.35;
    const predictable = /(?:19|20)\d{2}[!@#$%]*$/.test(lower);
    const noPatterns = !(sequential || repeated || repeatedPattern || lowDiversity);
    let score = (rules.length_points.find(([minimum]) => length >= minimum) || [0, 0])[1];
    score += Object.values(criteria).filter(Boolean).length * 10;
    if (length >= 8 && new Set(characters).size >= Math.min(length, 10)) score += 10;
    if (length >= 12 && noPatterns && !dictionary) score += 10;
    score -= 20 * sequential + 20 * repeated + 25 * repeatedPattern + 20 * lowDiversity;
    score -= 30 * dictionary + 10 * predictable;
    score = length ? Math.max(0, Math.min(100, score)) : 0;
    if (length < 8) score = Math.min(score, 24);
    if (common) score = Math.min(score, 10);
    if (dictionary) score = Math.min(score, 44);
    const checklist = {
      minimum_length: length >= 8, recommended_length: length >= 12, ...criteria,
      no_patterns: noPatterns && length > 0, not_common: !common && !dictionary && length > 0
    };
    const recommendations = [];
    if (length < 12) recommendations.push("Make it longer. Aim for at least 12–16 characters.");
    if (common || dictionary) recommendations.push("Replace common words and predictable substitutions with unrelated words or random characters.");
    if (!noPatterns) recommendations.push("Avoid sequences, keyboard runs, and repeated characters or short blocks.");
    if (predictable) recommendations.push("Avoid a year or date at the end of your password.");
    if (Object.values(criteria).filter(Boolean).length < 3) recommendations.push("Try a mix of character types, or a longer randomly chosen passphrase.");
    if (score > 0 && score < 85 && !recommendations.length) recommendations.push("Add length or use the generator for a less predictable password.");
    return { score, strength: names[[25, 45, 65, 85].filter(threshold => score >= threshold).length],
      password_length: length, criteria, checklist, criteria_passed: Object.values(checklist).filter(Boolean).length, recommendations };
  }

  function render() {
    if (!rules) return;
    result = analyze(input.value);
    revision++;
    const empty = !result.password_length;
    const index = names.indexOf(result.strength);
    const color = empty ? "#67758a" : colors[index];
    document.getElementById("score-value").textContent = empty ? "—" : result.score;
    const ring = document.getElementById("score-ring");
    ring.style.setProperty("--score", `${result.score}%`);
    ring.style.setProperty("--strength-color", color);
    const label = document.getElementById("strength-label");
    label.textContent = empty ? "Ready when you are" : result.strength;
    label.style.color = color;
    const progress = document.getElementById("strength-progress");
    progress.style.width = `${result.score}%`;
    progress.style.backgroundColor = color;
    document.querySelector(".strength-meter").setAttribute("aria-valuenow", String(result.score));
    const descriptions = ["A fresh start would make this much safer.", "A little more length and randomness will help.", "A good start. There’s room to make it stronger.", "Nice work. Add a little length for extra strength.", "Looking strong. Keep it unique to one account."];
    document.getElementById("strength-description").textContent = empty ? "Type a password to discover its strength." : descriptions[index];
    document.getElementById("password-length").textContent = result.password_length;
    document.getElementById("criteria-count").textContent = `${result.criteria_passed} of 8 met`;
    document.querySelectorAll("[data-criterion]").forEach(item => {
      const passed = result.checklist[item.dataset.criterion];
      item.classList.toggle("passed", passed);
      item.querySelector("i").className = `bi bi-${passed ? "check-circle-fill" : "circle"}`;
      item.querySelector(".criterion-status").textContent = passed ? "Met" : "Not met";
    });
    const list = document.getElementById("recommendations");
    list.replaceChildren();
    const suggestions = empty ? ["Your personalized recommendations will appear as you type."] : result.recommendations.length ? result.recommendations : ["No obvious weaknesses found. Keep it unique, store it in a password manager, and enable MFA."];
    suggestions.forEach(text => { const item = document.createElement("li"); item.textContent = text; list.append(item); });
    saveButton.disabled = empty;
    saveStatus.textContent = "";
  }
  window.PSC.bindVisibility(document.getElementById("password-toggle"), input);
  input.addEventListener("input", render);
  document.getElementById("clear-password").addEventListener("click", () => { input.value = ""; input.type = "password"; document.getElementById("password-toggle").setAttribute("aria-pressed", "false"); document.getElementById("password-toggle").setAttribute("aria-label", "Show password"); document.getElementById("password-toggle").innerHTML = '<i class="bi bi-eye" aria-hidden="true"></i>'; render(); input.focus(); });
  saveButton.addEventListener("click", async () => {
    if (!result || !result.password_length) return;
    const savedRevision = revision;
    const payload = { score: result.score, password_length: result.password_length, criteria: result.criteria };
    saveButton.disabled = true;
    saveStatus.textContent = "Saving anonymous metadata…";
    try {
      const response = await fetch("/api/analytics", {
        method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content },
        body: JSON.stringify(payload), cache: "no-store"
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not save this result. Please try again.");
      if (revision === savedRevision) saveStatus.textContent = data.message;
    } catch (error) {
      if (revision === savedRevision) { saveStatus.textContent = error.message; saveButton.disabled = false; }
    }
  });
  fetch("/static/data/scoring-rules.json", { cache: "no-store" }).then(response => { if (!response.ok) throw new Error(); return response.json(); }).then(data => {
    rules = data; input.disabled = false; render();
  }).catch(() => { document.getElementById("strength-description").textContent = "Couldn't load the checker. Refresh the page to try again."; });
  window.addEventListener("pagehide", () => { input.value = ""; result = null; });
  window.addEventListener("pageshow", render);
  window.PSC.analyze = password => analyze(password);
})();
