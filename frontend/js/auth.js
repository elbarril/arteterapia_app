// Authentication Module
const Auth = {
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    },

    /**
     * Get current user data
     */
    getCurrentUser() {
        const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
        return userData ? JSON.parse(userData) : null;
    },

    /**
     * Login user
     */
    async login(username, password) {
        try {
            const data = await api.post(API_ENDPOINTS.LOGIN, {
                username,
                password
            });

            // Store tokens and user data
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);
            localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(data.user));

            return { success: true, user: data.user };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);

        // Redirect to login
        UI.showPage('loginPage');
        UI.hideNavbar();
    },

    /**
     * Fetch current user from API
     */
    async fetchCurrentUser() {
        try {
            const user = await api.get(API_ENDPOINTS.ME);
            localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
            return user;
        } catch (error) {
            console.error('Failed to fetch user:', error);
            return null;
        }
    },

    /**
     * Initialize auth state
     */
    async init() {
        if (this.isAuthenticated()) {
            // Verify token is still valid
            const user = await this.fetchCurrentUser();
            if (user) {
                UI.showNavbar();
                UI.updateUserInfo(user);
                UI.showPage('workshopsPage');
                Workshops.loadWorkshops();
            } else {
                this.logout();
            }
        } else {
            UI.showPage('loginPage');
            UI.hideNavbar();
        }
    }
};
