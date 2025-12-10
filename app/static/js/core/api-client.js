/**
 * API Client - Centralized AJAX request handler
 * Provides a consistent interface for all HTTP requests with error handling
 */

class APIClient {
    /**
     * Make a POST request
     * @param {string} url - The endpoint URL
     * @param {Object} data - The data to send
     * @param {Object} options - Additional options (onLoading callback, etc.)
     * @returns {Promise<Object>} The response data
     */
    async post(url, data, options = {}) {
        const { onLoading } = options;

        try {
            if (onLoading) onLoading(true);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('API Error:', error);
            throw error;
        } finally {
            if (onLoading) onLoading(false);
        }
    }

    /**
     * Make a GET request
     * @param {string} url - The endpoint URL
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} The response data
     */
    async get(url, options = {}) {
        const { onLoading } = options;

        try {
            if (onLoading) onLoading(true);

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('API Error:', error);
            throw error;
        } finally {
            if (onLoading) onLoading(false);
        }
    }
}

// Export as singleton
const apiClient = new APIClient();
