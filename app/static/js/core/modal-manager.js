/**
 * Modal Manager - Handles Bootstrap modal interactions
 * Replaces native alert(), confirm(), and prompt() with Bootstrap modals
 */

class ModalManager {
    /**
     * Show an alert modal
     * @param {string} message - The message to display
     * @param {string} title - The modal title
     * @returns {Promise<void>} Resolves when modal is closed
     */
    alert(message, title = 'Mensaje') {
        return new Promise((resolve) => {
            const modalEl = document.getElementById('globalAlertModal');
            document.getElementById('globalAlertTitle').textContent = title;
            document.getElementById('globalAlertMessage').textContent = message;

            const modal = new bootstrap.Modal(modalEl);

            const onHidden = () => {
                modalEl.removeEventListener('hidden.bs.modal', onHidden);
                resolve();
            };
            modalEl.addEventListener('hidden.bs.modal', onHidden);

            modal.show();
        });
    }

    /**
     * Show a confirmation modal
     * @param {string} message - The message to display
     * @param {string} title - The modal title
     * @param {Object} options - Additional options (confirmBtnText, confirmBtnClass)
     * @returns {Promise<boolean>} Resolves with true if confirmed, false otherwise
     */
    confirm(message, title = 'Confirmación', options = {}) {
        const {
            confirmBtnText = 'Confirmar',
            confirmBtnClass = 'btn-danger'
        } = options;

        return new Promise((resolve) => {
            const modalEl = document.getElementById('globalConfirmModal');
            document.getElementById('globalConfirmTitle').textContent = title;
            document.getElementById('globalConfirmMessage').textContent = message;

            const confirmBtn = document.getElementById('globalConfirmBtn');
            confirmBtn.textContent = confirmBtnText;
            confirmBtn.className = `btn ${confirmBtnClass}`;

            const modal = new bootstrap.Modal(modalEl);
            let confirmed = false;

            // Remove existing listeners to prevent duplicates
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

            newConfirmBtn.onclick = () => {
                confirmed = true;
                modal.hide();
            };

            const onHidden = () => {
                modalEl.removeEventListener('hidden.bs.modal', onHidden);
                resolve(confirmed);
            };
            modalEl.addEventListener('hidden.bs.modal', onHidden);

            modal.show();
        });
    }

    /**
     * Show a prompt modal
     * @param {string} label - The input label
     * @param {string} defaultValue - The default input value
     * @param {string} title - The modal title
     * @returns {Promise<string|null>} Resolves with input value or null if cancelled
     */
    prompt(label, defaultValue = '', title = 'Ingresar Datos') {
        return new Promise((resolve) => {
            const modalEl = document.getElementById('globalPromptModal');
            const input = document.getElementById('globalPromptInput');
            const confirmBtn = document.getElementById('globalPromptBtn');

            document.getElementById('globalPromptTitle').textContent = title;
            document.getElementById('globalPromptLabel').textContent = label;
            input.value = defaultValue;

            const modal = new bootstrap.Modal(modalEl);
            let value = null;

            // Remove existing listeners
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

            // Handle Enter key
            input.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    newConfirmBtn.click();
                }
            };

            // Focus input when modal shown
            modalEl.addEventListener('shown.bs.modal', () => {
                input.focus();
            }, { once: true });

            newConfirmBtn.onclick = () => {
                value = input.value;
                modal.hide();
            };

            const onHidden = () => {
                modalEl.removeEventListener('hidden.bs.modal', onHidden);
                resolve(value);
            };
            modalEl.addEventListener('hidden.bs.modal', onHidden);

            modal.show();
        });
    }
}

// Export as singleton
const modalManager = new ModalManager();

// Also export as showModal for backward compatibility
const showModal = {
    alert: (message, title) => modalManager.alert(message, title),
    confirm: (message, title, options) => modalManager.confirm(message, title, options),
    prompt: (label, defaultValue, title) => modalManager.prompt(label, defaultValue, title)
};
