/*
================================================================================
                      OVERVIEW PAGE MODULE
================================================================================
Homepage: air health status, daily statistics, CO₂ thermometer.
================================================================================
*/

const isOverviewPage = !!document.querySelector(".air-health");
let lastSubPPM = null;
let overviewUpdateInterval = null;
let overviewUpdateSpeed = 5; // Default 5 seconds

/*
================================================================================
                      AIR HEALTH CARD
================================================================================
*/

function updateAirHealth(avgPPM) {
  const card = document.querySelector(".air-health");
  const status = document.getElementById("air-status");
  const advice = document.getElementById("air-advice");

  if (!card || !status || !advice) return;

  card.className = "card air-health";

  card.classList.remove("status-change");
  void card.offsetWidth; // force reflow
  card.classList.add("status-change");

  if (avgPPM < goodThreshold) {
    card.classList.add("good");
    status.textContent = "Excellent";
    advice.textContent = "Air sain, aucune action nécessaire";
  } else if (avgPPM < badThreshold) {
    card.classList.add("medium");
    status.textContent = "Acceptable";
    advice.textContent = "Surveillez la qualité de l'air";
  } else {
    card.classList.add("bad");
    status.textContent = "Mauvais";
    advice.textContent = "Aérez la pièce dès que possible";
  }
}

/*
================================================================================
                      SUB VALUE ANIMATION
================================================================================
*/

function animateSubValue(ppm, el) {
  if (!el) return;

  if (lastSubPPM === null) {
    el.textContent = `CO₂ actuel · ${ppm} ppm`;
    el.style.color = ppmColor(ppm);
    lastSubPPM = ppm;
    return;
  }

  const start = lastSubPPM;
  const startTime = performance.now();

  function animate(time) {
    const progress = Math.min((time - startTime) / VALUE_ANIMATION_DURATION, 1);
    const eased = easeOutCubic(progress);
    const current = Math.round(start + (ppm - start) * eased);

    el.textContent = `CO₂ actuel · ${current} ppm`;

    if (progress < 1) requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);
  el.style.color = ppmColor(ppm);

  if (lastSubPPM < badThreshold && ppm >= badThreshold) {
    el.classList.add("blink-warning");
    setTimeout(() => el.classList.remove("blink-warning"), 900);
  }

  lastSubPPM = ppm;
}

/*
================================================================================
                      CO₂ THERMOMETER
================================================================================
*/

function updateCO2Thermo(value) {
  const fill = document.getElementById("co2-fill");
  const label = document.getElementById("co2-mini-value");

  if (!fill || !label) return;

  const max = 2000;
  const percent = Math.min(value / max, 1) * 100;

  fill.style.height = percent + "%";
  label.textContent = value + " ppm";

  if (value < 800) {
    fill.style.background = "var(--good)";
  } else if (value < 1200) {
    fill.style.background = "var(--medium)";
  } else {
    fill.style.background = "var(--bad)";
  }
}

/*
================================================================================
                      STATS LOADING
================================================================================
*/

async function loadOverviewStats() {
  const avgEl = document.getElementById("avg-ppm");
  const maxEl = document.getElementById("max-ppm");
  const badEl = document.getElementById("bad-time");
  const statusEl = document.getElementById("air-status");
  const subEl = document.getElementById("air-sub");
  const airCard = document.querySelector(".air-health");
  const analysisEl = document.getElementById("analysis-status");
  const analysisWidget = document.getElementById("analysis-widget");
  const thresholdsEl = document.getElementById("co2-thresholds");

  if (!airCard || !statusEl) return;

  try {
    // Use cached settings from WebSocket or global state
    let settings = getCachedSettings();
    if (!settings) {
      // Use global state already loaded by loadSharedSettings()
      // No HTTP fallback here to avoid unnecessary requests
      settings = {
        analysis_running: analysisRunning || true,
        good_threshold: goodThreshold,
        bad_threshold: badThreshold
      };
    }
    
    updateNavAnalysisState(settings.analysis_running);

    /* ⏸ ANALYSIS PAUSED */
    if (!settings.analysis_running) {
      airCard.classList.remove("good", "medium", "bad");
      airCard.classList.add("paused");

      statusEl.textContent = "Analyse en pause";
      subEl.textContent = "Aucune donnée en cours";

      if (analysisEl) {
        analysisEl.textContent = "Pause";
        analysisWidget?.classList.remove("good");
        analysisWidget?.classList.add("paused");
      }

      if (avgEl) avgEl.textContent = "—";
      if (maxEl) maxEl.textContent = "—";
      if (badEl) badEl.textContent = "—";

      thresholdsEl.textContent = `${settings.good_threshold} / ${settings.bad_threshold} ppm`;

      updateCO2Thermo?.(0);
      return;
    }

    /* ▶️ ANALYSIS RUNNING */
    airCard.classList.remove("paused");
    analysisWidget?.classList.remove("paused");
    analysisWidget?.classList.add("good");

    if (analysisEl) {
      analysisEl.textContent = "Active";
    }

    thresholdsEl.textContent = `${settings.good_threshold} / ${settings.bad_threshold} ppm`;

    /* LIVE SNAPSHOT */
    const live = await fetchLatestData();

    if (live?.ppm != null) {
      updateAirHealth(live.ppm);
      updateCO2Thermo(live.ppm);
      animateSubValue(live.ppm, subEl);
    }

    /* TODAY HISTORY */
    const data = await fetchTodayHistory();
    if (!data.length) return;

    const values = data.map((d) => d.ppm);
    const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
    const max = Math.max(...values);
    const badMinutes = values.filter((v) => v >= badThreshold).length;

    if (avgEl) avgEl.textContent = `${avg} ppm`;
    if (maxEl) maxEl.textContent = `${max} ppm`;
    if (badEl) badEl.textContent = `${badMinutes} min`;
  } catch (e) {
    console.error("Overview stats failed", e);
  }
}

/*
================================================================================
                      INITIALIZATION
================================================================================
*/

function startOverviewRefresh() {
  if (overviewUpdateInterval) clearInterval(overviewUpdateInterval);
  loadOverviewStats();
  overviewUpdateInterval = setInterval(loadOverviewStats, overviewUpdateSpeed * 1000);
}

function stopOverviewRefresh() {
  if (overviewUpdateInterval) {
    clearInterval(overviewUpdateInterval);
    overviewUpdateInterval = null;
  }
}

// WebSocket handler for settings changes
window.handleOverviewSettings = function(settings) {
  if (settings.overview_update_speed !== undefined) {
    overviewUpdateSpeed = settings.overview_update_speed;
  }
  if (isOverviewPage) {
    startOverviewRefresh(); // Restart with new interval
  }
};

// WebSocket handler for CO₂ updates - DISABLED on overview page
// Overview uses a fixed interval timer (startOverviewRefresh) to avoid duplicate updates
window.handleOverviewCO2Update = function(data) {
  if (!isOverviewPage) return;
  // No-op: let the timer-based interval control updates
};

if (isOverviewPage) {
  document.addEventListener("DOMContentLoaded", async () => {
    // Load settings from server to get correct overview_update_speed
    try {
      const res = await fetch("/api/settings");
      const settings = await res.json();
      if (settings.overview_update_speed !== undefined) {
        overviewUpdateSpeed = settings.overview_update_speed;
      }
    } catch (e) {
      console.warn("Could not load settings, using default interval", e);
    }
    
    startOverviewRefresh();
  });
}

/*
================================================================================
                      EXPORT BUTTONS
================================================================================
*/

document.getElementById("export-day-csv")?.addEventListener("click", async () => {
  const data = await fetchTodayHistory();

  let csv = "time,ppm\n";
  data.forEach((d) => {
    const time = new Date(d.timestamp).toLocaleTimeString();
    csv += `${time},${d.ppm}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "rapport_journalier.csv";
  a.click();
});

document.getElementById("export-day-pdf")?.addEventListener("click", () => {
  window.open("/api/report/daily/pdf", "_blank");
});
