"use strict";
(async () => {
  const status = document.getElementById("chart-status");
  const charts = [];
  try {
    const response = await fetch("/admin/stats", { cache: "no-store", redirect: "error" });
    if (!response.ok) throw new Error();
    const stats = await response.json();
    if (!window.Chart) throw new Error();
    const colors = ["#ee7a88", "#efa16c", "#e5be63", "#68b6c8", "#4bbda0"];
    const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
    function axisColor() { return getComputedStyle(document.documentElement).getPropertyValue("--muted").trim(); }
    function gridColor() { return getComputedStyle(document.documentElement).getPropertyValue("--border").trim(); }
    const common = { responsive: true, maintainAspectRatio: false, animation: reducedMotion ? false : { duration: 600 }, plugins: { legend: { display: false } } };
    const axis = { grid: { color: gridColor(), drawTicks: false }, border: { display: false }, ticks: { color: axisColor(), font: { size: 9, family: "Segoe UI" }, padding: 10 } };
    charts.push(new Chart(document.getElementById("distribution-chart"), {
      type: "doughnut", data: { labels: stats.categories, datasets: [{ data: stats.counts, backgroundColor: colors, borderWidth: 0, hoverOffset: 3, spacing: 3, borderRadius: 3 }] }, options: { ...common, cutout: "78%" }
    }));
    charts.push(new Chart(document.getElementById("timeline-chart"), {
      type: "line", data: { labels: stats.dates, datasets: [{ label: "Checks", data: stats.daily_counts, borderColor: "#26a28c", backgroundColor: "#2dbb9d13", borderWidth: 2, fill: true, tension: 0.35, pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: "#26a28c" }] },
      options: { ...common, scales: { x: { ...axis, grid: { display: false } }, y: { ...axis, beginAtZero: true, ticks: { ...axis.ticks, precision: 0 } } } }
    }));
    charts.push(new Chart(document.getElementById("category-chart"), {
      type: "bar", data: { labels: ["V. weak", "Weak", "Medium", "Strong", "V. strong"], datasets: [{ label: "Checks", data: stats.counts, backgroundColor: colors, borderRadius: 5, maxBarThickness: 27 }] },
      options: { ...common, scales: { x: { ...axis, grid: { display: false }, ticks: { ...axis.ticks, font: { size: 8 }, maxRotation: 0, autoSkip: false } }, y: { ...axis, beginAtZero: true, ticks: { ...axis.ticks, precision: 0 } } } }
    }));
    if (!stats.total) status.textContent = "No records yet. Charts will populate after an anonymous result is saved.";
    document.addEventListener("themechange", () => {
      charts.forEach(chart => {
        if (chart.options.scales) Object.values(chart.options.scales).forEach(scale => { scale.ticks.color = axisColor(); if (scale.grid.display !== false) scale.grid.color = gridColor(); });
        chart.update("none");
      });
    });
  } catch (_) { status.textContent = "Charts couldn't load. Your statistics and records are still available above and below. Refresh or sign in again."; }
})();
