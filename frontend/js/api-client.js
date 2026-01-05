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
}

const api = new ApiClient();
window.orionApi = api;
