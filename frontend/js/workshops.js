// Workshops Module
const Workshops = {
    currentWorkshop: null,

    /**
     * Load all workshops
     */
    async loadWorkshops() {
        try {
            UI.showLoading('workshopsGrid', 'Cargando talleres...');

            const workshops = await api.get(API_ENDPOINTS.WORKSHOPS);

            if (workshops.length === 0) {
                UI.showEmpty('workshopsGrid', 'No hay talleres creados. ¡Crea tu primer taller!');
                return;
            }

            this.renderWorkshops(workshops);
        } catch (error) {
            UI.showError('workshopsGrid', `Error al cargar talleres: ${error.message}`);
            UI.showToast('Error al cargar talleres', 'error');
        }
    },

    /**
     * Render workshops grid
     */
    renderWorkshops(workshops) {
        const grid = document.getElementById('workshopsGrid');

        grid.innerHTML = workshops.map(workshop => `
            <div class="workshop-card" onclick="Workshops.viewWorkshop(${workshop.id})">
                <div class="workshop-card-header">
                    <h3 class="workshop-card-title">${UI.escapeHtml(workshop.name)}</h3>
                    <p class="workshop-card-objective">
                        ${workshop.objective ? UI.escapeHtml(workshop.objective) : 'Sin objetivo definido'}
                    </p>
                </div>
                <div class="workshop-card-footer">
                    <div class="workshop-stat">
                        <span>👥</span>
                        <span class="workshop-stat-value">${workshop.participant_count || 0}</span>
                        <span>participantes</span>
                    </div>
                    <div class="workshop-stat">
                        <span>📅</span>
                        <span class="workshop-stat-value">${workshop.session_count || 0}</span>
                        <span>sesiones</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    /**
     * View workshop details
     */
    async viewWorkshop(workshopId) {
        try {
            const workshop = await api.get(API_ENDPOINTS.WORKSHOP_DETAIL(workshopId));
            this.currentWorkshop = workshop;

            this.renderWorkshopDetail(workshop);
            UI.showPage('workshopDetailPage');

            // Load participants
            await Participants.loadParticipants(workshopId);

            // Load sessions
            const sessions = await Sessions.getWorkshopSessions(workshopId);
            Sessions.renderSessionsList(sessions, workshopId);
        } catch (error) {
            UI.showToast(`Error al cargar taller: ${error.message}`, 'error');
        }
    },

    /**
     * Render workshop detail
     */
    renderWorkshopDetail(workshop) {
        const detailContainer = document.getElementById('workshopDetail');

        detailContainer.innerHTML = `
            <h1>${UI.escapeHtml(workshop.name)}</h1>
            <p class="workshop-detail-objective">
                ${workshop.objective ? UI.escapeHtml(workshop.objective) : 'Sin objetivo definido'}
            </p>
            <div class="workshop-detail-meta">
                <div class="workshop-stat">
                    <span>Creado:</span>
                    <span class="workshop-stat-value">${UI.formatDate(workshop.created_at)}</span>
                </div>
                <div class="workshop-stat">
                    <span>👥</span>
                    <span class="workshop-stat-value">${workshop.participant_count || 0}</span>
                    <span>participantes</span>
                </div>
                <div class="workshop-stat">
                    <span>📅</span>
                    <span class="workshop-stat-value">${workshop.session_count || 0}</span>
                    <span>sesiones</span>
                </div>
            </div>
        `;

        // Render sessions if available
        if (workshop.sessions && workshop.sessions.length > 0) {
            this.renderSessions(workshop.sessions);
        } else {
            document.getElementById('sessionsList').innerHTML =
                '<div class="alert alert-info">No hay sesiones creadas</div>';
        }
    },

    /**
     * Render sessions list
     */
    renderSessions(sessions) {
        const sessionsList = document.getElementById('sessionsList');

        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-item">
                <div class="session-title">${UI.escapeHtml(session.prompt || 'Sin consigna')}</div>
                <p class="text-muted">${UI.escapeHtml(session.motivation || '')}</p>
                ${session.materials && session.materials.length > 0 ? `
                    <p class="text-muted">Materiales: ${session.materials.join(', ')}</p>
                ` : ''}
                <p class="text-muted">
                    ${session.observation_count || 0} observaciones
                </p>
            </div>
        `).join('');
    },

    /**
     * Show create workshop modal
     */
    showCreateModal() {
        const content = `
            <form id="createWorkshopForm">
                <div class="form-group">
                    <label for="workshopName">Nombre del Taller *</label>
                    <input type="text" id="workshopName" class="form-input" 
                           placeholder="Ej: Taller de Pintura" required>
                </div>
                <div class="form-group">
                    <label for="workshopObjective">Objetivo</label>
                    <textarea id="workshopObjective" class="form-textarea" 
                              placeholder="Describe el objetivo del taller..."></textarea>
                </div>
            </form>
        `;

        UI.showModal('Crear Nuevo Taller', content, [
            {
                text: 'Cancelar',
                class: 'btn-outline',
                onclick: 'UI.closeModal()'
            },
            {
                text: 'Crear Taller',
                class: 'btn-primary',
                onclick: 'Workshops.createWorkshop()'
            }
        ]);
    },

    /**
     * Create new workshop
     */
    async createWorkshop() {
        const name = document.getElementById('workshopName').value.trim();
        const objective = document.getElementById('workshopObjective').value.trim();

        if (!name) {
            UI.showToast('El nombre del taller es requerido', 'error');
            return;
        }

        try {
            const workshop = await api.post(API_ENDPOINTS.WORKSHOPS, {
                name,
                objective: objective || null
            });

            UI.closeModal();
            UI.showToast('Taller creado exitosamente', 'success');

            // Reload workshops
            await this.loadWorkshops();
        } catch (error) {
            UI.showToast(`Error al crear taller: ${error.message}`, 'error');
        }
    },

    /**
     * Show edit workshop modal
     */
    showEditModal() {
        if (!this.currentWorkshop) return;

        const content = `
            <form id="editWorkshopForm">
                <div class="form-group">
                    <label for="editWorkshopName">Nombre del Taller *</label>
                    <input type="text" id="editWorkshopName" class="form-input" 
                           value="${UI.escapeHtml(this.currentWorkshop.name)}" required>
                </div>
                <div class="form-group">
                    <label for="editWorkshopObjective">Objetivo</label>
                    <textarea id="editWorkshopObjective" class="form-textarea">${UI.escapeHtml(this.currentWorkshop.objective || '')}</textarea>
                </div>
            </form>
        `;

        UI.showModal('Editar Taller', content, [
            {
                text: 'Cancelar',
                class: 'btn-outline',
                onclick: 'UI.closeModal()'
            },
            {
                text: 'Guardar Cambios',
                class: 'btn-primary',
                onclick: 'Workshops.updateWorkshop()'
            }
        ]);
    },

    /**
     * Update workshop
     */
    async updateWorkshop() {
        if (!this.currentWorkshop) return;

        const name = document.getElementById('editWorkshopName').value.trim();
        const objective = document.getElementById('editWorkshopObjective').value.trim();

        if (!name) {
            UI.showToast('El nombre del taller es requerido', 'error');
            return;
        }

        try {
            const updated = await api.patch(
                API_ENDPOINTS.WORKSHOP_DETAIL(this.currentWorkshop.id),
                { name, objective: objective || null }
            );

            this.currentWorkshop = updated;
            UI.closeModal();
            UI.showToast('Taller actualizado exitosamente', 'success');

            // Refresh detail view
            this.renderWorkshopDetail(updated);
        } catch (error) {
            UI.showToast(`Error al actualizar taller: ${error.message}`, 'error');
        }
    },

    /**
     * Delete workshop
     */
    async deleteWorkshop() {
        if (!this.currentWorkshop) return;

        const content = `
            <p>¿Estás seguro de que deseas eliminar el taller 
               <strong>"${UI.escapeHtml(this.currentWorkshop.name)}"</strong>?</p>
            <p class="text-muted">Esta acción no se puede deshacer y eliminará todos los participantes, 
               sesiones y observaciones asociadas.</p>
        `;

        UI.showModal('Confirmar Eliminación', content, [
            {
                text: 'Cancelar',
                class: 'btn-outline',
                onclick: 'UI.closeModal()'
            },
            {
                text: 'Eliminar',
                class: 'btn-danger',
                onclick: 'Workshops.confirmDelete()'
            }
        ]);
    },

    /**
     * Confirm delete workshop
     */
    async confirmDelete() {
        if (!this.currentWorkshop) return;

        try {
            await api.delete(API_ENDPOINTS.WORKSHOP_DETAIL(this.currentWorkshop.id));

            UI.closeModal();
            UI.showToast('Taller eliminado exitosamente', 'success');

            // Go back to workshops list
            UI.showPage('workshopsPage');
            await this.loadWorkshops();
        } catch (error) {
            UI.showToast(`Error al eliminar taller: ${error.message}`, 'error');
        }
    }
};
