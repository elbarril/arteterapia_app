// Sessions Module
const Sessions = {
    /**
     * Get all sessions for a workshop
     */
    async getWorkshopSessions(workshopId) {
        try {
            return await api.get(API_ENDPOINTS.WORKSHOP_SESSIONS(workshopId));
        } catch (error) {
            UI.showToast(`Error loading sessions: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Get single session
     */
    async getSession(sessionId) {
        try {
            return await api.get(API_ENDPOINTS.SESSION_DETAIL(sessionId));
        } catch (error) {
            UI.showToast(`Error loading session: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Create new session
     */
    async createSession(workshopId, sessionData) {
        try {
            const data = {
                workshop_id: workshopId,
                prompt: sessionData.prompt,
                motivation: sessionData.motivation || null,
                materials: sessionData.materials || null
            };

            const session = await api.post(API_ENDPOINTS.SESSIONS, data);
            UI.showToast('Session created successfully', 'success');
            return session;
        } catch (error) {
            UI.showToast(`Error creating session: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Update session
     */
    async updateSession(sessionId, sessionData) {
        try {
            const data = {
                prompt: sessionData.prompt,
                motivation: sessionData.motivation || null,
                materials: sessionData.materials || null
            };

            const session = await api.patch(API_ENDPOINTS.SESSION_DETAIL(sessionId), data);
            UI.showToast('Session updated successfully', 'success');
            return session;
        } catch (error) {
            UI.showToast(`Error updating session: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Delete session
     */
    async deleteSession(sessionId) {
        try {
            const result = await api.delete(API_ENDPOINTS.SESSION_DETAIL(sessionId));
            UI.showToast('Session deleted successfully', 'success');
            return result;
        } catch (error) {
            UI.showToast(`Error deleting session: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Render sessions list
     */
    renderSessionsList(sessions, workshopId) {
        const container = document.getElementById('sessions-list');
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    No sessions found. Create your first session!
                </div>
            `;
            return;
        }

        const html = sessions.map(session => `
            <div class="card mb-3" data-session-id="${session.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h5 class="card-title">${this.escapeHtml(session.prompt)}</h5>
                            ${session.motivation ? `
                                <p class="card-text text-muted mb-2">
                                    <small><strong>Motivation:</strong> ${this.escapeHtml(session.motivation)}</small>
                                </p>
                            ` : ''}
                            ${session.materials && session.materials.length > 0 ? `
                                <p class="card-text mb-2">
                                    <small>
                                        <strong>Materials:</strong> 
                                        ${session.materials.map(m => `<span class="badge bg-secondary me-1">${this.escapeHtml(m)}</span>`).join('')}
                                    </small>
                                </p>
                            ` : ''}
                            <p class="card-text">
                                <small class="text-muted">
                                    <i class="bi bi-clipboard-check me-1"></i>
                                    ${session.observation_count} observation(s)
                                </small>
                            </p>
                        </div>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="Sessions.editSession(${session.id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="Sessions.confirmDeleteSession(${session.id}, ${workshopId})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    },

    /**
     * Show create session modal
     */
    showCreateModal(workshopId) {
        const content = `
            <form id="sessionForm">
                <div class="form-group">
                    <label for="sessionPrompt">Consigna *</label>
                    <textarea id="sessionPrompt" class="form-textarea" 
                              placeholder="Ej: Dibuja cómo te sientes hoy" required></textarea>
                </div>
                <div class="form-group">
                    <label for="sessionMotivation">Motivación</label>
                    <textarea id="sessionMotivation" class="form-textarea" 
                              placeholder="Describe la motivación de la sesión..."></textarea>
                </div>
                <div class="form-group">
                    <label for="sessionMaterials">Materiales</label>
                    <input type="text" id="sessionMaterials" class="form-input" 
                           placeholder="Ej: lápices, papel, colores (separados por comas)">
                </div>
            </form>
        `;

        UI.showModal('Crear Sesión', content, [
            {
                text: 'Cancelar',
                class: 'btn-outline',
                onclick: 'UI.closeModal()'
            },
            {
                text: 'Crear Sesión',
                class: 'btn-primary',
                onclick: `Sessions.handleCreateSession(${workshopId})`
            }
        ]);
    },

    /**
     * Handle create session
     */
    async handleCreateSession(workshopId) {
        const prompt = document.getElementById('sessionPrompt').value.trim();
        const motivation = document.getElementById('sessionMotivation').value.trim();
        const materials = document.getElementById('sessionMaterials').value.trim();

        if (!prompt) {
            UI.showToast('La consigna es requerida', 'error');
            return;
        }

        try {
            await this.createSession(workshopId, { prompt, motivation, materials });
            UI.closeModal();

            // Refresh sessions list
            const sessions = await this.getWorkshopSessions(workshopId);
            this.renderSessionsList(sessions, workshopId);
        } catch (error) {
            console.error('Error creating session:', error);
        }
    },

    /**
     * Edit session
     */
    async editSession(sessionId) {
        try {
            const session = await this.getSession(sessionId);

            const content = `
                <form id="sessionForm">
                    <div class="form-group">
                        <label for="sessionPrompt">Consigna *</label>
                        <textarea id="sessionPrompt" class="form-textarea" required>${this.escapeHtml(session.prompt)}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="sessionMotivation">Motivación</label>
                        <textarea id="sessionMotivation" class="form-textarea">${this.escapeHtml(session.motivation || '')}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="sessionMaterials">Materiales</label>
                        <input type="text" id="sessionMaterials" class="form-input" 
                               value="${session.materials ? this.escapeHtml(session.materials.join(', ')) : ''}">
                    </div>
                </form>
            `;

            UI.showModal('Editar Sesión', content, [
                {
                    text: 'Cancelar',
                    class: 'btn-outline',
                    onclick: 'UI.closeModal()'
                },
                {
                    text: 'Guardar Cambios',
                    class: 'btn-primary',
                    onclick: `Sessions.handleUpdateSession(${sessionId}, ${session.workshop_id})`
                }
            ]);
        } catch (error) {
            console.error('Error loading session for edit:', error);
        }
    },

    /**
     * Handle update session
     */
    async handleUpdateSession(sessionId, workshopId) {
        const prompt = document.getElementById('sessionPrompt').value.trim();
        const motivation = document.getElementById('sessionMotivation').value.trim();
        const materials = document.getElementById('sessionMaterials').value.trim();

        if (!prompt) {
            UI.showToast('La consigna es requerida', 'error');
            return;
        }

        try {
            await this.updateSession(sessionId, { prompt, motivation, materials });
            UI.closeModal();

            // Refresh sessions list
            const sessions = await this.getWorkshopSessions(workshopId);
            this.renderSessionsList(sessions, workshopId);
        } catch (error) {
            console.error('Error updating session:', error);
        }
    },

    /**
     * Confirm delete session
     */
    confirmDeleteSession(sessionId, workshopId) {
        if (confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
            this.deleteSessionAndRefresh(sessionId, workshopId);
        }
    },

    /**
     * Delete session and refresh list
     */
    async deleteSessionAndRefresh(sessionId, workshopId) {
        try {
            await this.deleteSession(sessionId);
            const sessions = await this.getWorkshopSessions(workshopId);
            this.renderSessionsList(sessions, workshopId);
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    },

    /**
     * Handle session form submit
     */
    async handleSessionFormSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const sessionId = form.dataset.sessionId;
        const workshopId = form.dataset.workshopId;

        const sessionData = {
            prompt: document.getElementById('sessionPrompt').value.trim(),
            motivation: document.getElementById('sessionMotivation').value.trim(),
            materials: document.getElementById('sessionMaterials').value.trim()
        };

        try {
            if (sessionId) {
                await this.updateSession(sessionId, sessionData);
            } else {
                await this.createSession(workshopId, sessionData);
            }

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('sessionModal'));
            modal.hide();

            // Refresh sessions list
            const sessions = await this.getWorkshopSessions(workshopId);
            this.renderSessionsList(sessions, workshopId);
        } catch (error) {
            console.error('Error saving session:', error);
        }
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
