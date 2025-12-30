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
    loadOverviewStats();
    setInterval(loadOverviewStats, OVERVIEW_REFRESH_INTERVAL);
  }

  console.log("✓ Morpheus app loaded");
})();
