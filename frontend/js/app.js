// Main Application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize authentication
    Auth.init();

    // Setup event listeners
    setupEventListeners();
});

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });
    }

    // Navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;

            if (page === 'workshops') {
                UI.showPage('workshopsPage');
                Workshops.loadWorkshops();
            } else if (page === 'profile') {
                UI.showPage('profilePage');
                loadProfile();
            }
        });
    });

    // Create workshop button
    const createWorkshopBtn = document.getElementById('createWorkshopBtn');
    if (createWorkshopBtn) {
        createWorkshopBtn.addEventListener('click', () => {
            Workshops.showCreateModal();
        });
    }

    // Back to workshops button
    const backToWorkshopsBtn = document.getElementById('backToWorkshopsBtn');
    if (backToWorkshopsBtn) {
        backToWorkshopsBtn.addEventListener('click', () => {
            UI.showPage('workshopsPage');
            Workshops.loadWorkshops();
        });
    }

    // Edit workshop button
    const editWorkshopBtn = document.getElementById('editWorkshopBtn');
    if (editWorkshopBtn) {
        editWorkshopBtn.addEventListener('click', () => {
            Workshops.showEditModal();
        });
    }

    // Delete workshop button
    const deleteWorkshopBtn = document.getElementById('deleteWorkshopBtn');
    if (deleteWorkshopBtn) {
        deleteWorkshopBtn.addEventListener('click', () => {
            Workshops.deleteWorkshop();
        });
    }

    // Add participant button
    const addParticipantBtn = document.getElementById('addParticipantBtn');
    if (addParticipantBtn) {
        addParticipantBtn.addEventListener('click', () => {
            Participants.showAddModal();
        });
    }

    // Add session button
    const addSessionBtn = document.getElementById('addSessionBtn');
    if (addSessionBtn) {
        addSessionBtn.addEventListener('click', () => {
            if (Workshops.currentWorkshop) {
                Sessions.showCreateModal(Workshops.currentWorkshop.id);
            }
        });
    }
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const loginError = document.getElementById('loginError');

    // Hide previous errors
    loginError.style.display = 'none';

    // Validate
    if (!username || !password) {
        loginError.textContent = 'Por favor ingresa usuario y contraseña';
        loginError.style.display = 'block';
        return;
    }

    // Disable button
    loginBtn.disabled = true;
    loginBtn.textContent = 'Iniciando sesión...';

    try {
        const result = await Auth.login(username, password);

        if (result.success) {
            // Update UI
            UI.showNavbar();
            UI.updateUserInfo(result.user);
            UI.showPage('workshopsPage');

            // Load workshops
            await Workshops.loadWorkshops();

            // Show success message
            UI.showToast('¡Bienvenido!', 'success');
        } else {
            loginError.textContent = result.error || 'Error al iniciar sesión';
            loginError.style.display = 'block';
        }
    } catch (error) {
        loginError.textContent = 'Error de conexión. Por favor intenta nuevamente.';
        loginError.style.display = 'block';
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Iniciar Sesión';
    }
}

/**
 * Load user profile
 */
async function loadProfile() {
    const user = Auth.getCurrentUser();
    if (!user) return;

    const profileCard = document.getElementById('profileCard');

    profileCard.innerHTML = `
        <div class="profile-info">
            <div class="profile-field">
                <div class="profile-label">Usuario</div>
                <div class="profile-value">${UI.escapeHtml(user.username)}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Email</div>
                <div class="profile-value">${UI.escapeHtml(user.email)}</div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Rol</div>
                <div class="profile-value">
                    ${user.roles.includes('admin') ? 'Administrador' : 'Editor'}
                </div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Estado de la cuenta</div>
                <div class="profile-value">
                    ${user.active ? '✅ Activa' : '❌ Inactiva'}
                </div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Email verificado</div>
                <div class="profile-value">
                    ${user.email_verified ? '✅ Verificado' : '⚠️ No verificado'}
                </div>
            </div>
            <div class="profile-field">
                <div class="profile-label">Miembro desde</div>
                <div class="profile-value">${UI.formatDate(user.created_at)}</div>
            </div>
        </div>
    `;
}
