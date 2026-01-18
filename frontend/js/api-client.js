/**
 * Orion Emergency Module - API Client
 * Shared wrapper for backend API calls
 */

const API_BASE_URL = '/api';

class ApiClient {
    /**
     * Helper for making fetch requests
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Request Failed: ${endpoint}`, error);
            throw error;
        }
    }

    // --- Core Endpoints ---

    async getSymptoms() {
        return this.request('/sintomas');
    }

    async getQuestions(sintoma) {
        return this.request(`/preguntas/${encodeURIComponent(sintoma)}`);
    }

    async classifyTriage(data) {
        return this.request('/triage', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getMetrics() {
        // Fallback for metrics implementation
        try {
            return await this.request('/metrics');
        } catch (e) {
            console.warn('Metrics endpoint not available, using simulation data');
            return null;
        }
    }

    async getPredictionAccuracy() {
        // Mock data for visualization
        // In prod this would hit: return this.request('/metrics/prediction_accuracy');
        return {
            drift_report: {
                status: "active",
                drift_percentage: 15.4,
                alert: false
            },
            graph_data: {
                labels: ["-5h", "-4h", "-3h", "-2h", "-1h", "Now"],
                predicted: [12, 14, 15, 14, 16, 18],
                actual: [11, 13, 16, 14, 19, 17]
            }
        };
    }
}

const api = new ApiClient();
window.orionApi = api;
