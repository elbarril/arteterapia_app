// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api/v1',
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3
};

// Storage keys
const STORAGE_KEYS = {
    ACCESS_TOKEN: 'arteterapia_access_token',
    REFRESH_TOKEN: 'arteterapia_refresh_token',
    USER_DATA: 'arteterapia_user_data'
};

// API Endpoints
const API_ENDPOINTS = {
    // Auth
    LOGIN: '/auth/login',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',

    // Workshops
    WORKSHOPS: '/workshops',
    WORKSHOP_DETAIL: (id) => `/workshops/${id}`,

    // Participants
    PARTICIPANTS: '/participants',
    PARTICIPANT_DETAIL: (id) => `/participants/${id}`,
    WORKSHOP_PARTICIPANTS: (workshopId) => `/participants/workshop/${workshopId}`,
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, STORAGE_KEYS, API_ENDPOINTS };
}
