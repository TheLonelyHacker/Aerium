/*
================================================================================
                        LIVE PAGE MODULE
================================================================================
Real-time CO₂ monitoring: chart, animations, polling, live data updates.
================================================================================
*/

let chart;
let lastPPM = null;
let lastQualityPPM = null;
let lastRotation = 0;
let pollingDelay = POLLING_INTERVAL;
let pollInterval = null;
let analysisRunningLocal = true;

const valueEl = document.getElementById("value");
const trendEl = document.getElementById("trend");
const qualityEl = document.getElementById("quality");
const chartCanvas = document.getElementById("chart");
const pausedOverlay = document.getElementById("paused-overlay");
const exportBtn = document.getElementById("export");
const resetBtn = document.getElementById("reset-btn");

const isLivePage = !!(valueEl && qualityEl && chartCanvas);

/*
================================================================================
                      CHART PLUGIN & SETUP
================================================================================
*/

/* ─────────────────────────────────────────────────────────────────────────── 
   Chart Background Plugin (Zone Visualization)
──────────────────────────────────────────────────────────────────────────── */
const zoneBackgroundPlugin = {
  id: "zoneBackground",
  beforeDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    if (!chartArea) return;

    const { top, bottom, left, right } = chartArea;
    const y = scales.y;

    const good = prevGoodThreshold + (goodThreshold - prevGoodThreshold) * bgFade;
    const bad = prevBadThreshold + (badThreshold - prevBadThreshold) * bgFade;

    const yGood = y.getPixelForValue(good);
    const yBad = y.getPixelForValue(bad);

    const gradient = ctx.createLinearGradient(0, top, 0, bottom);
    const gStop = (yGood - top) / (bottom - top);
    const bStop = (yBad - top) / (bottom - top);

    if (good === bad) {
      gradient.addColorStop(0, "rgba(248,113,113,0.20)");
      gradient.addColorStop(bStop, "rgba(248,113,113,0.15)");
      gradient.addColorStop(bStop, "rgba(74,222,128,0.18)");
      gradient.addColorStop(1, "rgba(74,222,128,0.12)");
    } else {
      gradient.addColorStop(0, "rgba(248,113,113,0.20)");
      gradient.addColorStop(bStop, "rgba(248,113,113,0.15)");
      gradient.addColorStop(bStop, "rgba(250,204,21,0.18)");
      gradient.addColorStop(gStop, "rgba(250,204,21,0.15)");
      gradient.addColorStop(gStop, "rgba(74,222,128,0.18)");
      gradient.addColorStop(1, "rgba(74,222,128,0.12)");
    }

    ctx.save();
    ctx.fillStyle = gradient;
    ctx.fillRect(left, top, right - left, bottom - top);
    ctx.restore();
  },
};

if (typeof Chart !== "undefined") {
  Chart.register(zoneBackgroundPlugin);
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Chart Creation
──────────────────────────────────────────────────────────────────────────── */
function createChart() {
  chart = new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "CO₂",
          data: [],
          normalized: true,
          borderWidth: 3,
          tension: 0.35,
          fill: true,
          backgroundColor: "rgba(11,13,18,0.30)",
          borderColor: "#9ca3af",

          animations: {
            y: {
              from: (ctx) => {
                if (!ctx || ctx.parsed == null) return undefined;

                const data = ctx.chart.data.datasets[0].data;
                const i = ctx.dataIndex;

                if (i === data.length - 1 && data.length > 1) {
                  return data[i - 1];
                }

                return ctx.parsed.y;
              },
              duration: 400,
              easing: "easeOutCubic",
            },

            fill: {
              duration: 0,
            },
          },

          segment: {
            borderColor: (ctx) => {
              const v = ctx.p1?.parsed?.y;
              return v == null ? "#9ca3af" : ppmColor(v);
            },
          },
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBorderColor: "#0b0d12",
          pointBackgroundColor: (ctx) => {
            const v = ctx.parsed?.y;
            return v == null ? "#9ca3af" : ppmColor(v);
          },
        },
      ],
    },
    options: {
      responsive: true,
      animation: { duration: 0 },
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          min: 400,
          max: 2000,
          animation: false,
          grid: { color: "rgba(255,255,255,0.06)" },
        },
        x: {
          animation: false,
          grid: { color: "rgba(255,255,255,0.04)" },
        },
      },
    },
  });
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Chart Updates
──────────────────────────────────────────────────────────────────────────── */
function updateChart(ppm) {
  if (!chart) return;

  const timeLabel = new Date(Date.now()).toLocaleTimeString();

  chart.data.labels.push(timeLabel);
  chart.data.datasets[0].data.push(ppm);

  chart.update({ duration: 0 });

  if (chart.data.labels.length > MAX_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
    chart.update("none");
  }
}

/*
================================================================================
                      OVERLAY & UI
================================================================================
*/

function showPausedOverlay() {
  pausedOverlay?.classList.add("active");
  valueEl.textContent = "⏸";
  valueEl.style.color = "#9ca3af";
  trendEl.textContent = "";
  qualityEl.textContent = "Analyse en pause";
  qualityEl.style.color = "#9ca3af";
  qualityEl.style.background = "rgba(255,255,255,0.08)";
}

function hidePausedOverlay() {
  pausedOverlay?.classList.remove("active");
}

/*
================================================================================
                      ANIMATIONS
================================================================================
*/

function animateValue(ppm) {
  if (lastPPM === null) {
    valueEl.textContent = `${ppm} ppm`;
    valueEl.style.color = ppmColor(ppm);
    lastPPM = ppm;
    return;
  }

  const start = lastPPM;
  const startTime = performance.now();

  function frame(time) {
    const t = Math.min((time - startTime) / CHART_ANIMATION_DURATION, 1);
    const eased = easeOutCubic(t);
    const current = Math.round(start + (ppm - start) * eased);
    valueEl.textContent = `${current} ppm`;
    if (t < 1) requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
  valueEl.style.color = ppmColor(ppm);

  lastPPM = ppm;
}

function updateTrend(prev, current) {
  if (prev === null) return;

  let target = current > prev ? -45 : current < prev ? 45 : 0;
  if (target <= lastRotation) target += 360;

  trendEl.style.transform = `rotate(${target}deg)`;
  trendEl.style.color = ppmColor(current);
  lastRotation = target;
}

function animateQuality(ppm) {
  if (!qualityEl) return;

  const color = ppmColor(ppm);
  const label = qualityText(ppm);

  qualityEl.textContent = label;
  qualityEl.style.color = color;
  qualityEl.style.background = color + "22";
  qualityEl.style.border = `1px solid ${color}55`;
  qualityEl.style.boxShadow = `0 0 12px ${color}33`;

  if (
    lastQualityPPM !== null &&
    lastQualityPPM < badThreshold &&
    ppm >= badThreshold
  ) {
    qualityEl.classList.add("blink-warning");
    setTimeout(() => qualityEl.classList.remove("blink-warning"), 900);
  }

  lastQualityPPM = ppm;
}

/*
================================================================================
                      SETTINGS & POLLING
================================================================================
*/

async function loadLiveSettings() {
  const res = await fetch("/api/settings");
  const s = await res.json();

  prevGoodThreshold = goodThreshold;
  prevBadThreshold = badThreshold;

  goodThreshold = Math.min(s.good_threshold, 2000 - 50);
  badThreshold = Math.min(s.bad_threshold, 2000);

  updatePollingSpeed(s.update_speed || 1);

  bgFade = 0;

  const start = performance.now();
  const duration = 500;

  function animateFade(time) {
    const t = Math.min((time - start) / duration, 1);
    bgFade = easeOutCubic(t);
    chart.update("none");
    if (t < 1) requestAnimationFrame(animateFade);
  }

  requestAnimationFrame(animateFade);
}

function startPolling() {
  if (!analysisRunningLocal) return;
  stopPolling();
  pollInterval = setInterval(poll, pollingDelay);
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

function updatePollingSpeed(seconds) {
  pollingDelay = seconds * 1000;
  startPolling();
}

/*
================================================================================
                      POLLING & DATA
================================================================================
*/

async function poll() {
  const data = await fetchLatestData();

  /* ⏸ PAUSE HANDLING */
  if (data.analysis_running === false) {
    analysisRunningLocal = false;
    updateNavAnalysisState(false);
    hidePausedOverlay();
    showPausedOverlay();
    stopPolling();
    return;
  }

  /* ▶️ RESUME HANDLING */
  if (!analysisRunningLocal && data.analysis_running === true) {
    analysisRunningLocal = true;
    updateNavAnalysisState(true);
    hidePausedOverlay();
    startPolling();
  }

  if (!analysisRunningLocal) return;

  if (isLivePage) hidePausedOverlay();

  if (!data || data.ppm == null) return;

  const ppm = data.ppm;
  console.log("New PPM", ppm);

  if (isLivePage) {
    updateTrend(lastPPM, ppm);
    animateValue(ppm);
    animateQuality(ppm);
    updateChart(ppm);
  }
}

/*
================================================================================
                      INITIALIZATION
================================================================================
*/

function initLivePage() {
  if (!isLivePage) return;

  analysisRunningLocal = true;
  createChart();
  loadLiveSettings();
  poll();
  startPolling();
}

/* ─────────────────────────────────────────────────────────────────────────── 
   Button Handlers
──────────────────────────────────────────────────────────────────────────── */
exportBtn?.addEventListener("click", () => {
  let csv = "time,ppm\n";
  chart.data.labels.forEach((t, i) => {
    csv += `${t},${chart.data.datasets[0].data[i]}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "co2_history.csv";
  a.click();
});

resetBtn?.addEventListener("click", () => {
  chart.data.labels = [];
  chart.data.datasets[0].data = [];
  chart.update();
});

if (isLivePage) {
  document.addEventListener("DOMContentLoaded", initLivePage);
}
