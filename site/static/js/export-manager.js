// Export Manager JavaScript - Gestion d'Exports

document.addEventListener('DOMContentLoaded', function() {
    initializeExportManager();
});

function initializeExportManager() {
    // Load initial data
    loadSensors();
    loadScheduledExports();
}

function loadSensors() {
    // Fetch available sensors from the server
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const sensorSelect = document.getElementById('sensorSelect');
            
            if (sensorSelect) {
                sensorSelect.innerHTML = '<option value="">Sélectionnez un capteur...</option>';
                if (data.length && Array.isArray(data)) {
                    data.forEach(sensor => {
                        const option = document.createElement('option');
                        option.value = sensor.id;
                        option.textContent = sensor.name;
                        sensorSelect.appendChild(option);
                    });
                } else {
                    // Fallback if API returns empty
                    const option = document.createElement('option');
                    option.value = 'default';
                    option.textContent = 'Capteur par défaut';
                    sensorSelect.appendChild(option);
                }
            }
        })
        .catch(error => {
            console.error('Erreur chargement des capteurs:', error);
            // Add default sensor option on error
            const sensorSelect = document.getElementById('sensorSelect');
            if (sensorSelect) {
                const option = document.createElement('option');
                option.value = 'default';
                option.textContent = 'Capteur par défaut';
                sensorSelect.appendChild(option);
            }
        });
}

function exportData(format) {
    const sensorId = document.getElementById('sensorSelect')?.value || 'default';
    const period = document.getElementById('periodSelect')?.value || '7';
    
    if (!sensorId || sensorId === '') {
        alert('Veuillez sélectionner un capteur');
        return;
    }
    
    // Show loading state
    const btn = event?.target;
    const originalText = btn ? btn.textContent : 'Export';
    if (btn) {
        btn.textContent = 'Chargement...';
        btn.disabled = true;
    }
    
    // Call simulated export endpoint
    fetch('/api/export/simulate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            format: format,
            period_days: parseInt(period),
            sensor_id: sensorId
        })
    })
    .then(response => {
        if (format === 'csv') {
            // Handle CSV download
            return response.text().then(text => {
                downloadFile(text, `co2_export_${period}d.csv`, 'text/csv');
                if (btn) {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }
                showExportSuccess(format, period);
            });
        } else {
            return response.json().then(data => {
                if (data.success) {
                    if (format === 'json') {
                        downloadFile(JSON.stringify(data.data, null, 2), `co2_export_${period}d.json`, 'application/json');
                    } else if (format === 'excel') {
                        alert('Export Excel: ' + data.records + ' enregistrements préparés');
                    } else if (format === 'pdf') {
                        alert('Export PDF: ' + data.records + ' enregistrements préparés');
                    }
                    if (btn) {
                        btn.textContent = originalText;
                        btn.disabled = false;
                    }
                    showExportSuccess(format, period);
                } else {
                    alert('Erreur: ' + (data.error || 'Export échoué'));
                    if (btn) {
                        btn.textContent = originalText;
                        btn.disabled = false;
                    }
                }
            });
        }
    })
    .catch(error => {
        console.error('Erreur export:', error);
        alert('Erreur: ' + error.message);
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
}

function quickExportData() {
    const format = document.getElementById('quickExportFormat')?.value || 'csv';
    const resultDiv = document.getElementById('quick-export-result');
    
    if (resultDiv) {
        resultDiv.innerHTML = '<div class="loading">Génération de l\'export...</div>';
        resultDiv.style.display = 'block';
    }
    
    fetch('/api/export/simulate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            format: format,
            period_days: 30
        })
    })
    .then(response => {
        if (format === 'csv') {
            return response.text().then(text => {
                downloadFile(text, `co2_export_30d.csv`, 'text/csv');
                if (resultDiv) {
                    resultDiv.innerHTML = '<div class="success"><strong>✓ Export réussi!</strong> Fichier CSV téléchargé.</div>';
                }
            });
        } else {
            return response.json().then(data => {
                if (data.success) {
                    if (format === 'json') {
                        downloadFile(JSON.stringify(data.data, null, 2), `co2_export_30d.json`, 'application/json');
                    }
                    if (resultDiv) {
                        resultDiv.innerHTML = `<div class="success"><strong>✓ Export réussi!</strong> ${data.records} enregistrements exportés en ${format.toUpperCase()}.</div>`;
                    }
                } else {
                    if (resultDiv) {
                        resultDiv.innerHTML = `<div class="error">Erreur: ${data.error || 'Export échoué'}</div>`;
                    }
                }
            });
        }
    })
    .catch(error => {
        console.error('Erreur export rapide:', error);
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="error">Erreur: ${error.message}</div>`;
        }
    });
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function showExportSuccess(format, days) {
    const message = `Export ${format.toUpperCase()} réussi! Fichier téléchargé.`;
    // You could show a toast notification here
    console.log(message);
}

function loadScheduledExports() {
    fetch('/api/export/scheduled')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('scheduled-exports-list');
            if (container && data.exports) {
                if (data.exports.length === 0) {
                    container.innerHTML = '<p style="color: #9ca3af;">Aucun export programmé</p>';
                } else {
                    let html = '<div class="scheduled-exports">';
                    data.exports.forEach(exp => {
                        html += `
                            <div class="export-item">
                                <h4>${exp.format.toUpperCase()} - ${exp.frequency}</h4>
                                <p>Prochaine exécution: ${exp.next_execution || 'Bientôt'}</p>
                                <button onclick="deleteScheduledExport(${exp.id})" class="btn-delete">Supprimer</button>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;
                }
            }
        })
        .catch(error => console.error('Erreur chargement exports programmés:', error));
}

function scheduleExport() {
    const format = document.getElementById('schedule-format')?.value || 'csv';
    const frequency = document.getElementById('schedule-frequency')?.value || 'weekly';
    
    if (!format || !frequency) {
        alert('Veuillez sélectionner un format et une fréquence');
        return;
    }
    
    fetch('/api/export/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            format: format,
            frequency: frequency
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Export programmé: ${format} - ${frequency}`);
            loadScheduledExports();
            // Reset form
            document.getElementById('schedule-format').value = 'csv';
            document.getElementById('schedule-frequency').value = 'weekly';
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de programmer l\'export'));
        }
    })
    .catch(error => {
        console.error('Erreur programmation export:', error);
        alert('Erreur: ' + error.message);
    });
}

function deleteScheduledExport(exportId) {
    if (!confirm('Êtes-vous sûr?')) return;
    
    fetch(`/api/export/scheduled/${exportId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadScheduledExports();
        } else {
            alert('Erreur: Impossible de supprimer l\'export');
        }
    })
    .catch(error => {
        console.error('Erreur suppression export:', error);
        alert('Erreur: ' + error.message);
    });
}

function scheduleExport() {
    const sensorId = document.getElementById('schedule-sensor')?.value;
    const format = document.getElementById('schedule-format')?.value;
    const frequency = document.getElementById('schedule-frequency')?.value;
    const email = document.getElementById('schedule-email')?.value;
    
    if (!sensorId || !format || !frequency || !email) {
        alert('Please fill all fields');
        return;
    }
    
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Scheduling...';
    btn.disabled = true;
    
    fetch('/api/advanced/export/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensor_id: sensorId,
            format: format,
            frequency: frequency,
            email: email
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Schedule failed');
        return response.json();
    })
    .then(data => {
        // Reset form
        document.getElementById('schedule-form').reset();
        
        // Refresh scheduled exports list
        loadScheduledExports();
        showNotification('Export scheduled successfully!', 'success');
    })
    .catch(error => {
        console.error('Schedule error:', error);
        showNotification('Schedule failed: ' + error.message, 'error');
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function loadExportHistory() {
    fetch('/api/advanced/export/history')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('.history-table table tbody');
            if (!tbody || !data.history) return;
            
            tbody.innerHTML = '';
            
            if (data.history.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No exports yet</td></tr>';
                return;
            }
            
            data.history.forEach(export_item => {
                const row = document.createElement('tr');
                const date = new Date(export_item.created_at).toLocaleString();
                
                row.innerHTML = `
                    <td>${export_item.sensor_name}</td>
                    <td>${export_item.format.toUpperCase()}</td>
                    <td>${date}</td>
                    <td><span class="status ${export_item.status.toLowerCase()}">${export_item.status}</span></td>
                    <td>
                        ${export_item.file_url ? `<a href="${export_item.file_url}" download>Download</a>` : '-'}
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading export history:', error));
}

function loadScheduledExports() {
    fetch('/api/advanced/export/scheduled')
        .then(response => response.json())
        .then(data => {
            const container = document.querySelector('.scheduled-list');
            if (!container || !data.scheduled) return;
            
            container.innerHTML = '';
            
            if (data.scheduled.length === 0) {
                container.innerHTML = '<p class="text-muted">No scheduled exports</p>';
                return;
            }
            
            data.scheduled.forEach(schedule => {
                const item = document.createElement('div');
                item.className = 'scheduled-item';
                
                item.innerHTML = `
                    <div class="scheduled-item-info">
                        <h4>${schedule.sensor_name}</h4>
                        <p><strong>Frequency:</strong> ${schedule.frequency}</p>
                        <p><strong>Format:</strong> ${schedule.format.toUpperCase()}</p>
                        <p><strong>Email:</strong> ${schedule.email}</p>
                    </div>
                    <div class="scheduled-item-actions">
                        <button class="btn btn-secondary" onclick="editScheduledExport(${schedule.id})">Edit</button>
                        <button class="btn" style="background: #dc3545; color: white;" onclick="deleteScheduledExport(${schedule.id})">Delete</button>
                    </div>
                `;
                
                container.appendChild(item);
            });
        })
        .catch(error => console.error('Error loading scheduled exports:', error));
}

function editScheduledExport(scheduleId) {
    // Implementation for editing scheduled export
    fetch(`/api/advanced/export/scheduled/${scheduleId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('schedule-sensor').value = data.sensor_id;
            document.getElementById('schedule-format').value = data.format;
            document.getElementById('schedule-frequency').value = data.frequency;
            document.getElementById('schedule-email').value = data.email;
            
            // Scroll to form
            document.getElementById('schedule-form').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => console.error('Error loading schedule:', error));
}

function deleteScheduledExport(scheduleId) {
    if (!confirm('Are you sure you want to delete this scheduled export?')) {
        return;
    }
    
    fetch(`/api/advanced/export/scheduled/${scheduleId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) throw new Error('Delete failed');
        loadScheduledExports();
        showNotification('Scheduled export deleted', 'success');
    })
    .catch(error => {
        console.error('Delete error:', error);
        showNotification('Delete failed: ' + error.message, 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        color: white;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add slide animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
