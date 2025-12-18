// UI Module
const UI = {
    /**
     * Show a specific page
     */
    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
        });

        // Show requested page
        const page = document.getElementById(pageId);
        if (page) {
            page.style.display = 'block';
        }

        // Update nav links
        this.updateNavLinks(pageId);
    },

    /**
     * Update active nav link
     */
    updateNavLinks(pageId) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page && pageId.includes(link.dataset.page)) {
                link.classList.add('active');
            }
        });
    },

    /**
     * Show/hide navbar
     */
    showNavbar() {
        document.getElementById('navbar').style.display = 'block';
    },

    hideNavbar() {
        document.getElementById('navbar').style.display = 'none';
    },

    /**
     * Update user info in navbar
     */
    updateUserInfo(user) {
        document.getElementById('userName').textContent = user.username;
        const roleText = user.roles.includes('admin') ? 'Administrador' : 'Editor';
        document.getElementById('userRole').textContent = roleText;
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<div class="toast-message">${message}</div>`;

        container.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /**
     * Show modal
     */
    showModal(title, content, actions = []) {
        const modal = document.getElementById('modal');
        const modalContent = document.getElementById('modalContent');

        let actionsHTML = '';
        if (actions.length > 0) {
            actionsHTML = `
                <div class="modal-footer">
                    ${actions.map(action => `
                        <button class="btn ${action.class || 'btn-primary'}" 
                                onclick="${action.onclick}"
                                ${action.id ? `id="${action.id}"` : ''}>
                            ${action.text}
                        </button>
                    `).join('')}
                </div>
            `;
        }

        modalContent.innerHTML = `
            <div class="modal-header">
                <h3>${title}</h3>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            ${actionsHTML}
        `;

        modal.classList.add('active');

        // Close on overlay click
        document.getElementById('modalOverlay').onclick = () => this.closeModal();
    },

    /**
     * Close modal
     */
    closeModal() {
        document.getElementById('modal').classList.remove('active');
    },

    /**
     * Show loading state
     */
    showLoading(elementId, message = 'Cargando...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-info">${message}</div>`;
        }
    },

    /**
     * Show error state
     */
    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-error">${message}</div>`;
        }
    },

    /**
     * Show empty state
     */
    showEmpty(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-info">${message}</div>`;
        }
    },

    /**
     * Format date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
