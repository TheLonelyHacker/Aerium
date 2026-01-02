/*
================================================================================
                  MORPHEUS CO₂ MONITORING - ENTRY POINT
================================================================================
Main application entry point that coordinates module loading and initialization.
Individual pages load their own feature modules (live.js, overview.js, etc).

Module loading order (see base.html):
  1. utils.js       - Shared utilities, constants, state management
  2. settings.js    - Settings page functionality
  3. analytics.js   - Analytics page functionality
  4. live.js        - Live page functionality
  5. overview.js    - Overview/home page functionality
  6. main.js        - This file (minimal entry point)
================================================================================
*/

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initGlobalState();
  initWebSocket(); // Initialize WebSocket connection
  initNavSparkline();
});

// Bootstrap application
(async () => {
  // Load shared settings and initialize global state
  await loadSharedSettings();
  const state = await loadSystemState();
  updateNavAnalysisState(state.analysis_running);

  // Start system state watcher for navbar updates
  startSystemStateWatcher();

  // Initialize analytics CSV import if on analytics page
  initAnalyticsCSVImport();

  // Initialize page-specific modules
  if (isLivePage) initLivePage();
  if (isOverviewPage) {
    // Initialize overview update speed from settings
    const ovSettings = getCachedSettings();
    if (ovSettings && ovSettings.overview_update_speed) {
      overviewUpdateSpeed = ovSettings.overview_update_speed;
    }
    startOverviewRefresh(); // Use dynamic interval based on settings
  }

  console.log("✓ Morpheus app loaded");
  console.log("🔧 Settings loaded:", getCachedSettings());
})();

/*
================================================================================
                      NAVBAR SPARKLINE (PPM)
================================================================================
*/

const NAV_SPARK_MAX = 40;
let navSparkValues = [];

function drawNavSparkline() {
  const canvas = document.getElementById("nav-ppm-spark");
  const valueEl = document.getElementById("nav-ppm-value");
  if (!canvas || !valueEl || !navSparkValues.length) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const min = Math.min(...navSparkValues);
  const max = Math.max(...navSparkValues);
  const range = Math.max(max - min, 1);

  ctx.strokeStyle = "#4ade80";
  ctx.lineWidth = 2;
  ctx.beginPath();

  navSparkValues.forEach((v, i) => {
    const x = (i / Math.max(navSparkValues.length - 1, 1)) * (w - 2) + 1;
    const norm = (v - min) / range;
    const y = h - norm * (h - 2) - 1;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.stroke();
}

function pushNavPpm(ppm) {
  const valueEl = document.getElementById("nav-ppm-value");
  if (valueEl && typeof ppm === "number") {
    valueEl.textContent = `${ppm} ppm`;
  }

  if (typeof ppm !== "number" || Number.isNaN(ppm)) return;
  navSparkValues.push(ppm);
  if (navSparkValues.length > NAV_SPARK_MAX) navSparkValues.shift();
  drawNavSparkline();
}

window.pushNavPpm = pushNavPpm;

async function initNavSparkline() {
  const canvas = document.getElementById("nav-ppm-spark");
  const valueEl = document.getElementById("nav-ppm-value");
  if (!canvas || !valueEl) return;

  try {
    const res = await fetch("/api/history/latest/40");
    const data = await res.json();
    const values = data.map((d) => d.ppm).filter((v) => typeof v === "number" && !Number.isNaN(v));
    navSparkValues = values.slice(-NAV_SPARK_MAX);
    if (navSparkValues.length) {
      valueEl.textContent = `${navSparkValues[navSparkValues.length - 1]} ppm`;
    }
    drawNavSparkline();
  } catch (e) {
    console.warn("Nav sparkline load failed", e);
  }
}
