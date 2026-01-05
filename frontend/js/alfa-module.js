/**
 * Orion Alfa - Administrative Module Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initAlfaModule();
});

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
