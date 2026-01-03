/*
================================================================================
                        ALERTS MANAGEMENT SYSTEM
================================================================================
Manages alert display across all pages with a persistent panel and navbar badge
*/

let alertsList = [];

document.addEventListener('DOMContentLoaded', () => {
  // Get DOM elements
  const alertsBtn = document.getElementById('alerts-btn');
  const closeAlertsBtn = document.getElementById('close-alerts-btn');
  const alertsPanel = document.getElementById('alerts-panel');
  const alertsList_elem = document.getElementById('alerts-list');
  const alertBadge = document.getElementById('alert-badge');

  // Toggle alerts panel
  if (alertsBtn) {
    alertsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      alertsPanel.classList.toggle('open');
    });
  }

  if (closeAlertsBtn) {
    closeAlertsBtn.addEventListener('click', () => {
      alertsPanel.classList.remove('open');
    });
  }

  // Close panel when clicking outside
  document.addEventListener('click', (e) => {
    if (!alertsPanel.contains(e.target) && !alertsBtn.contains(e.target)) {
      alertsPanel.classList.remove('open');
    }
  });

  // Listen for alert updates from other parts of the app
  window.addEventListener('alert-updated', (e) => {
    const alert = e.detail;
    addAlertToPanel(alert);
  });

  // Function to add alert to panel
  function addAlertToPanel(alert) {
    alertsList.unshift(alert); // Add to front
    if (alertsList.length > 20) alertsList.pop(); // Keep last 20

    // Update badge
    const count = alertsList.length;
    if (count > 0) {
      alertBadge.textContent = count;
      alertBadge.style.display = 'flex';
    }

    // Update panel
    renderAlerts();
  }

  // Function to render alerts in the panel
  function renderAlerts() {
    if (alertsList.length === 0) {
      alertsList_elem.innerHTML = '<p class="no-alerts">Aucune alerte pour le moment</p>';
      return;
    }

    alertsList_elem.innerHTML = alertsList.map((alert, index) => {
      const time = new Date(alert.timestamp).toLocaleTimeString('fr-FR');
      const levelClass = alert.type === 'threshold_exceeded' ? 'warning' :
                         alert.type === 'recovery' ? 'success' : 'error';
      
      return `
        <div class="alert-item ${levelClass}" data-index="${index}">
          <div>${alert.message}</div>
          <span class="alert-item-time">${time}</span>
          <button class="alert-item-close" onclick="removeAlert(${index})">✕</button>
        </div>
      `;
    }).join('');
  }

  // Function to remove alert (called from alert-item-close button)
  window.removeAlert = function(index) {
    alertsList.splice(index, 1);
    
    // Update badge
    const count = alertsList.length;
    if (count > 0) {
      alertBadge.textContent = count;
    } else {
      alertBadge.style.display = 'none';
    }
    
    renderAlerts();
  };

  // Initial render
  if (alertsList.length === 0) {
    alertsList_elem.innerHTML = '<p class="no-alerts">Aucune alerte pour le moment</p>';
  }
});
