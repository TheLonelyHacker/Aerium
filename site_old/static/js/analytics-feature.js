function loadPredictions() {
    const hours = document.getElementById('pred-hours')?.value || 2;
    const container = document.getElementById('predictions-container');
    container.innerHTML = '<div class="loading">Chargement des prédictions pour les ' + hours + ' prochaines heures...</div>';
    
    fetch('/api/analytics/predictions?hours=' + hours)
        .then(r => r.json())
        .then(data => {
            if (data.success && data.predictions) {
                let html = '<div class="data-display">';
                html += '<h3>Prédictions pour les ' + hours + ' Prochaines Heures</h3>';
                html += '<div class="prediction-list">';
                data.predictions.forEach((pred, i) => {
                    html += `<div class="prediction-item">
                        <span class="pred-time">+${pred.hour}h</span>
                        <span class="pred-value">${pred.predicted_co2.toFixed(1)} ppm</span>
                        <span class="pred-confidence">(${pred.confidence}% confiance)</span>
                        <span class="pred-bar" style="width: ${(pred.predicted_co2/1500)*100}%"></span>
                    </div>`;
                });
                html += '</div>';
                html += '<p class="info-text">Basé sur les modèles historiques et les tendances actuelles</p>';
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="error">Impossible de charger les prédictions</div>';
            }
        })
        .catch(e => {
            container.innerHTML = '<div class="error">Erreur: ' + e.message + '</div>';
        });
}

function loadAnomalies() {
    const container = document.getElementById('anomalies-container');
    container.innerHTML = '<div class="loading">Détection des anomalies...</div>';
    
    fetch('/api/analytics/anomalies')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.anomalies) {
                let html = '<div class="data-display">';
                html += '<h3>Anomalies Détectées</h3>';
                if (data.anomalies.length === 0) {
                    html += '<p class="success">✓ Aucune anomalie détectée - Vos données sont normales!</p>';
                } else {
                    html += '<div class="anomaly-list">';
                    data.anomalies.forEach((anom, i) => {
                        html += `<div class="anomaly-item severity-${anom.severity}">
                            <div class="anomaly-header">
                                <span class="anomaly-type">${anom.type}</span>
                                <span class="anomaly-severity">${anom.severity.toUpperCase()}</span>
                            </div>
                            <p class="anomaly-description">${anom.description}</p>
                            <span class="anomaly-value">Valeur: ${anom.value} ppm</span>
                            <span class="anomaly-time">${new Date(anom.timestamp).toLocaleString()}</span>
                        </div>`;
                    });
                    html += '</div>';
                }
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="error">Impossible de détecter les anomalies</div>';
            }
        })
        .catch(e => {
            container.innerHTML = '<div class="error">Erreur: ' + e.message + '</div>';
        });
}

function loadInsights() {
    const container = document.getElementById('insights-container');
    container.innerHTML = '<div class="loading">Génération des perspectives...</div>';
    
    fetch('/api/analytics/insights')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.insights) {
                let html = '<div class="data-display">';
                html += '<h3>Perspectives Générées par l\'IA</h3>';
                html += '<div class="insights-list">';
                data.insights.forEach((insight, i) => {
                    html += `<div class="insight-item">
                        <div class="insight-header">
                            <h4>${insight.title}</h4>
                            <span class="insight-impact">${insight.impact}</span>
                        </div>
                        <p class="insight-description">${insight.description}</p>
                        <p class="insight-recommendation"><strong>Recommandation:</strong> ${insight.recommendation}</p>
                    </div>`;
                });
                html += '</div>';
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="error">Impossible de générer les perspectives</div>';
            }
        })
        .catch(e => {
            container.innerHTML = '<div class="error">Erreur: ' + e.message + '</div>';
        });
}

// Load initial data when page loads
window.addEventListener('load', () => {
    loadPredictions();
    loadAnomalies();
    loadInsights();
});


function loadHealth() {
    const container = document.getElementById('health-container');
    container.innerHTML = '<div class="loading">Loading health recommendations...</div>';
    
    fetch('/api/health/recommendations')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.recommendations) {
                let html = '<div class="data-display">';
                html += '<h3>Your Health Recommendations</h3>';
                html += '<div class="recommendations-list">';
                data.recommendations.forEach((rec, i) => {
                    html += `<div class="recommendation-item">
                        <div class="rec-icon">${rec.category === 'action' ? '→' : '📋'}</div>
                        <div class="rec-content">
                            <h4>${rec.title}</h4>
                            <p>${rec.description}</p>
                            <span class="rec-priority">${rec.priority}</span>
                        </div>
                    </div>`;
                });
                html += '</div>';
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="error">Could not load recommendations</div>';
            }
        })
        .catch(e => {
            container.innerHTML = '<div class="error">Error: ' + e.message + '</div>';
        });
}

// Load initial data
window.addEventListener('load', () => {
    loadPredictions();
    loadAnomalies();
    loadInsights();
    loadHealth();
});
