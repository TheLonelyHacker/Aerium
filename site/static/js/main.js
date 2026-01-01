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
