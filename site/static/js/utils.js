/*
================================================================================
                        SHARED UTILITIES
================================================================================
Common functions used across all modules: animations, color logic, API calls,
state management.
================================================================================
*/

/*
================================================================================
                      CONFIGURATION & CONSTANTS
================================================================================
*/
const MAX_POINTS = 25;
const DEFAULT_GOOD_THRESHOLD = 800;
const DEFAULT_MEDIUM_THRESHOLD = 1200;
const DEFAULT_BAD_THRESHOLD = 1200;
const POLLING_INTERVAL = 1000; // ms
const STATE_SYNC_INTERVAL = 2000; // ms
const OVERVIEW_REFRESH_INTERVAL = 5000; // ms
const CHART_ANIMATION_DURATION = 450; // ms
const VALUE_ANIMATION_DURATION = 500; // ms

/*
================================================================================
                        GLOBAL STATE
================================================================================
*/
let goodThreshold = DEFAULT_GOOD_THRESHOLD;
let mediumThreshold = DEFAULT_MEDIUM_THRESHOLD;
let badThreshold = DEFAULT_BAD_THRESHOLD;

let prevGoodThreshold = goodThreshold;
let prevBadThreshold = badThreshold;

let analysisRunning = true;
let bgFade = 1;

/*
================================================================================
                    UTILITY FUNCTIONS
================================================================================
*/

/* ─────────────────────────────────────────────────────────────────────────── 
   Animation Easing
──────────────────────────────────────────────────────────────────────────── */
function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

function forceLayout(el) {
  el.getBoundingClientRect();
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Color & Value Interpolation
──────────────────────────────────────────────────────────────────────────── */
function lerp(a, b, t) {
  return a + (b - a) * t;
}

function lerpColor(c1, c2, t) {
  return `rgb(
    ${Math.round(lerp(c1[0], c2[0], t))},
    ${Math.round(lerp(c1[1], c2[1], t))},
    ${Math.round(lerp(c1[2], c2[2], t))}
  )`;
}

function ppmColor(ppm) {
  if (goodThreshold === badThreshold) {
    return ppm < goodThreshold ? "#4ade80" : "#f87171";
  }

  if (ppm < goodThreshold) return "#4ade80";
  if (ppm < badThreshold) return "#facc15";
  return "#f87171";
}

function ppmColorSmooth(ppm) {
  const green = [74, 222, 128];
  const yellow = [250, 204, 21];
  const red = [248, 113, 113];

  if (ppm <= goodThreshold) return `rgb(${green})`;

  if (ppm <= badThreshold) {
    const t = (ppm - goodThreshold) / (badThreshold - goodThreshold);
    return lerpColor(green, yellow, t);
  }

  const t = Math.min((ppm - badThreshold) / badThreshold, 1);
  return lerpColor(yellow, red, t);
}

function qualityText(ppm) {
  if (goodThreshold === badThreshold) {
    return ppm < goodThreshold ? "Bon" : "Mauvais";
  }

  if (ppm < goodThreshold) return "Bon";
  if (ppm < badThreshold) return "Moyen";
  return "Mauvais";
}

/*
================================================================================
                      API & DATA FETCHING
================================================================================
*/

/* ─────────────────────────────────────────────────────────────────────────── 
   System State API
──────────────────────────────────────────────────────────────────────────── */
async function loadSystemState() {
  const res = await fetch("/api/settings");
  return await res.json();
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Settings API
──────────────────────────────────────────────────────────────────────────── */
async function loadSharedSettings() {
  try {
    const res = await fetch("/api/settings");
    const s = await res.json();

    goodThreshold = s.good_threshold;
    badThreshold = s.bad_threshold;
    mediumThreshold = badThreshold;
  } catch {
    console.warn("Failed to load shared settings");
  }
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Live Data API
──────────────────────────────────────────────────────────────────────────── */
async function fetchLatestData() {
  const res = await fetch("/api/latest", {
    cache: "no-store",
  });
  return await res.json();
}

/* ─────────────────────────────────────────────────────────────────────────── 
   History API
──────────────────────────────────────────────────────────────────────────── */
async function fetchTodayHistory() {
  const res = await fetch("/api/history/today");
  return await res.json();
}

/*
================================================================================
                    AIR QUALITY LOGIC
================================================================================
*/

function getAirQuality(ppm) {
  if (ppm < goodThreshold) {
    return {
      level: "good",
      label: "Bon",
      advice: "Air sain",
      color: "var(--good)",
    };
  }

  if (ppm < badThreshold) {
    return {
      level: "medium",
      label: "Moyen",
      advice: "Air correct",
      color: "var(--medium)",
    };
  }

  return {
    level: "bad",
    label: "Mauvais",
    advice: "Aérez immédiatement",
    color: "var(--bad)",
  };
}

/*
================================================================================
                    SYSTEM STATE MANAGEMENT
================================================================================
*/

function updateNavAnalysisState(isRunning) {
  // Navbar
  const nav = document.getElementById("nav-analysis");
  const label = document.getElementById("nav-analysis-label");

  // Overview system pill
  const pill = document.querySelector(".system-pill");

  // Navbar update
  if (nav && label) {
    nav.classList.remove("is-running", "is-paused");

    if (isRunning) {
      nav.classList.add("is-running");
      label.textContent = "Analyse active";
    } else {
      nav.classList.add("is-paused");
      label.textContent = "Analyse en pause";
    }
  }

  // Overview pill update (safe even if not on overview page)
  if (pill) {
    pill.classList.toggle("running", isRunning);
    pill.classList.toggle("paused", !isRunning);
    pill.innerHTML = `<span class="dot"></span> ${
      isRunning ? "Analyse active" : "Analyse en pause"
    }`;
  }
}

function startSystemStateWatcher() {
  setInterval(async () => {
    try {
      const state = await loadSystemState();
      updateNavAnalysisState(state.analysis_running);
    } catch {
      console.warn("Failed to refresh system state");
    }
  }, STATE_SYNC_INTERVAL);
}

async function refreshSystemState() {
  try {
    const state = await loadSystemState();
    updateNavAnalysisState(state.analysis_running);
  } catch {
    console.warn("State sync failed");
  }
}

function initGlobalState() {
  refreshSystemState();
  setInterval(refreshSystemState, STATE_SYNC_INTERVAL);
}

/*
================================================================================
                      NAVBAR MANAGEMENT
================================================================================
*/

function initNavbar() {
  const navCenter = document.querySelector(".nav-center");
  const underline = document.querySelector(".nav-underline");
  const links = navCenter?.querySelectorAll("a");

  if (!navCenter || !underline) return;

  const path = window.location.pathname;

  function getActiveLink() {
    return [...links].find((link) => link.getAttribute("href") === path);
  }

  function moveUnderline(el) {
    if (!el) return;
    const r = el.getBoundingClientRect();
    const p = navCenter.getBoundingClientRect();
    underline.style.width = `${r.width}px`;
    underline.style.left = `${r.left - p.left}px`;
    underline.style.opacity = "1";
  }

  const active = getActiveLink();
  if (active) {
    active.classList.add("active");
    requestAnimationFrame(() => moveUnderline(active));
  }

  links.forEach((l) =>
    l.addEventListener("mouseenter", () => moveUnderline(l))
  );

  navCenter.addEventListener("mouseleave", () =>
    moveUnderline(getActiveLink())
  );

  window.addEventListener("resize", () => moveUnderline(getActiveLink()));
}

/*
================================================================================
                      INITIALIZATION BOOTSTRAP
================================================================================
*/

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initGlobalState();
});

(async () => {
  await loadSharedSettings();
  const state = await loadSystemState();
  updateNavAnalysisState(state.analysis_running);
  startSystemStateWatcher();
})();
