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
    CHANGE_PASSWORD: '/auth/change-password',

    // Workshops
    WORKSHOPS: '/workshops',
    WORKSHOP_DETAIL: (id) => `/workshops/${id}`,

    // Participants
    PARTICIPANTS: '/participants',
    PARTICIPANT_DETAIL: (id) => `/participants/${id}`,
    WORKSHOP_PARTICIPANTS: (workshopId) => `/participants/workshop/${workshopId}`,

    // Sessions
    SESSIONS: '/sessions',
    SESSION_DETAIL: (id) => `/sessions/${id}`,
    WORKSHOP_SESSIONS: (workshopId) => `/sessions/workshop/${workshopId}`,

    // Observations
    OBSERVATIONS: '/observations',
    OBSERVATION_DETAIL: (id) => `/observations/${id}`,
    WORKSHOP_OBSERVATIONS: (workshopId) => `/observations/workshop/${workshopId}`,
    OBSERVATION_INITIALIZE: '/observations/initialize',
    OBSERVATION_SAVE: '/observations/save',
    OBSERVATION_QUESTIONS: '/observations/questions',
    OBSERVATION_QUESTION: (index) => `/observations/questions/${index}`,
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, STORAGE_KEYS, API_ENDPOINTS };
}
