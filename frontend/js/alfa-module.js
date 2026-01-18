/**
 * Orion Alfa - Administrative Module Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initAlfaModule();
});

let accuracyChart = null;

async function initAlfaModule() {
    console.log('🔷 Orion Alfa Module Initialized');

    // Initial fetch
    updateMetrics();

    // Poll every 5 seconds
    setInterval(updateMetrics, 5000);
}

async function updateMetrics() {
    try {
        const metrics = await window.orionApi.getMetrics();
        if (metrics) {
            updateDashboard(metrics);
        }

        const accuracyData = await window.orionApi.getPredictionAccuracy();
        if (accuracyData) {
            updateAccuracyChart(accuracyData);
        }
    } catch (error) {
        console.error('Failed to update metrics', error);
    }
}

function updateDashboard(metrics) {
    // Helper to animate numbers
    const animateValue = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.innerText = value;
    };

    if (metrics.triage_count !== undefined) {
        // Find element for total triage or mapping
        // For now logging as we need to ID elements in HTML
        console.log('Metrics update:', metrics);
    }

    // Maps API metric keys to DOM IDs (need to add these IDs to HTML)
    const mappings = {
        'metric-mae': metrics.accuracy,
        'metric-latency': `${metrics.latency_ms}ms`,
        'metric-epoch': `EPOCH: ${metrics.epoch}`,
    };

    for (const [id, val] of Object.entries(mappings)) {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    }
}

function updateAccuracyChart(data) {
    const ctx = document.getElementById('accuracyChart');
    if (!ctx) return;

    // Alert Logic
    const alertEl = document.getElementById('drift-alert');
    if (data.drift_report.drift_percentage > 20 || data.drift_report.alert) {
        alertEl.classList.remove('hidden');
    } else {
        alertEl.classList.add('hidden');
    }

    if (!accuracyChart) {
        accuracyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.graph_data.labels,
                datasets: [
                    {
                        label: 'Predicted',
                        data: data.graph_data.predicted,
                        borderColor: '#00F0FF', // Primary Neon Cyan
                        backgroundColor: 'rgba(0, 240, 255, 0.1)',
                        tension: 0.4,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Actual',
                        data: data.graph_data.actual,
                        borderColor: '#E2E8F0', // Slate 200
                        backgroundColor: 'transparent',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false, // Disable animation for updates to prevent flicker
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Rajdhani' } }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#64748b' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748b' }
                    }
                }
            }
        });
    } else {
        // Update data
        accuracyChart.data.labels = data.graph_data.labels;
        accuracyChart.data.datasets[0].data = data.graph_data.predicted;
        accuracyChart.data.datasets[1].data = data.graph_data.actual;
        accuracyChart.update();
    }
}
