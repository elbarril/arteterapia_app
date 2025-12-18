// Participants Module
const Participants = {
    /**
     * Load participants for a workshop
     */
    async loadParticipants(workshopId) {
        try {
            const participants = await api.get(API_ENDPOINTS.WORKSHOP_PARTICIPANTS(workshopId));

            if (participants.length === 0) {
                UI.showEmpty('participantsList', 'No hay participantes en este taller');
                return;
            }

            this.renderParticipants(participants);
        } catch (error) {
            UI.showError('participantsList', `Error al cargar participantes: ${error.message}`);
        }
    },

    /**
     * Render participants list
     */
    renderParticipants(participants) {
        const list = document.getElementById('participantsList');

        list.innerHTML = participants.map(participant => `
            <div class="participant-item">
                <div class="participant-name">${UI.escapeHtml(participant.name)}</div>
                ${participant.extra_data && Object.keys(participant.extra_data).length > 0 ? `
                    <p class="text-muted">
                        ${Object.entries(participant.extra_data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(' | ')}
                    </p>
                ` : ''}
                <div class="participant-actions">
                    <button class="btn btn-sm btn-outline" 
                            onclick="Participants.showEditModal(${participant.id}, '${UI.escapeHtml(participant.name).replace(/'/g, "\\'")}')">
                        Editar
                    </button>
                    <button class="btn btn-sm btn-danger" 
                            onclick="Participants.deleteParticipant(${participant.id})">
                        Eliminar
                    </button>
                </div>
            </div>
        `).join('');
    },

    /**
     * Show add participant modal
     */
    showAddModal() {
        if (!Workshops.currentWorkshop) return;

        const content = `
            <form id="addParticipantForm">
                <div class="form-group">
                    <label for="participantName">Nombre del Participante *</label>
                    <input type="text" id="participantName" class="form-input" 
                           placeholder="Ej: Juan Pérez" required>
                </div>
                <div class="form-group">
                    <label for="participantAge">Edad (opcional)</label>
                    <input type="number" id="participantAge" class="form-input" 
                           placeholder="Ej: 25">
                </div>
                <div class="form-group">
                    <label for="participantNotes">Notas (opcional)</label>
                    <textarea id="participantNotes" class="form-textarea" 
                              placeholder="Información adicional..."></textarea>
                </div>
            </form>
        `;

        UI.showModal('Agregar Participante', content, [
            {
                text: 'Cancelar',
                class: 'btn-outline',
                onclick: 'UI.closeModal()'
            },
            {
                text: 'Agregar',
                class: 'btn-primary',
                onclick: 'Participants.addParticipant()'
            }
        ]);
    },

    /**
     * Add new participant
     */
    async addParticipant() {
        if (!Workshops.currentWorkshop) return;

        const name = document.getElementById('participantName').value.trim();
        const age = document.getElementById('participantAge').value;
        const notes = document.getElementById('participantNotes').value.trim();

        if (!name) {
            UI.showToast('El nombre del participante es requerido', 'error');
            return;
        }

        const extraData = {};
        if (age) extraData.age = parseInt(age);
        if (notes) extraData.notes = notes;

        try {
            await api.post(API_ENDPOINTS.PARTICIPANTS, {
                workshop_id: Workshops.currentWorkshop.id,
                name,
                extra_data: extraData
            });

            UI.closeModal();
            UI.showToast('Participante agregado exitosamente', 'success');

            // Reload participants
            await this.loadParticipants(Workshops.currentWorkshop.id);

            // Refresh workshop detail to update count
            await Workshops.viewWorkshop(Workshops.currentWorkshop.id);
        } catch (error) {
            UI.showToast(`Error al agregar participante: ${error.message}`, 'error');
        }
    },

    /**
     * Show edit participant modal
     */
    async showEditModal(participantId, currentName) {
        try {
            const participant = await api.get(API_ENDPOINTS.PARTICIPANT_DETAIL(participantId));

            const content = `
                <form id="editParticipantForm">
                    <div class="form-group">
                        <label for="editParticipantName">Nombre del Participante *</label>
                        <input type="text" id="editParticipantName" class="form-input" 
                               value="${UI.escapeHtml(participant.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="editParticipantAge">Edad (opcional)</label>
                        <input type="number" id="editParticipantAge" class="form-input" 
                               value="${participant.extra_data?.age || ''}">
                    </div>
                    <div class="form-group">
                        <label for="editParticipantNotes">Notas (opcional)</label>
                        <textarea id="editParticipantNotes" class="form-textarea">${participant.extra_data?.notes || ''}</textarea>
                    </div>
                </form>
            `;

            UI.showModal('Editar Participante', content, [
                {
                    text: 'Cancelar',
                    class: 'btn-outline',
                    onclick: 'UI.closeModal()'
                },
                {
                    text: 'Guardar Cambios',
                    class: 'btn-primary',
                    onclick: `Participants.updateParticipant(${participantId})`
                }
            ]);
        } catch (error) {
            UI.showToast(`Error al cargar participante: ${error.message}`, 'error');
        }
    },

    /**
     * Update participant
     */
    async updateParticipant(participantId) {
        const name = document.getElementById('editParticipantName').value.trim();
        const age = document.getElementById('editParticipantAge').value;
        const notes = document.getElementById('editParticipantNotes').value.trim();

        if (!name) {
            UI.showToast('El nombre del participante es requerido', 'error');
            return;
        }

        const extraData = {};
        if (age) extraData.age = parseInt(age);
        if (notes) extraData.notes = notes;

        try {
            await api.patch(API_ENDPOINTS.PARTICIPANT_DETAIL(participantId), {
                name,
                extra_data: extraData
            });

            UI.closeModal();
            UI.showToast('Participante actualizado exitosamente', 'success');

            // Reload participants
            if (Workshops.currentWorkshop) {
                await this.loadParticipants(Workshops.currentWorkshop.id);
            }
        } catch (error) {
            UI.showToast(`Error al actualizar participante: ${error.message}`, 'error');
        }
    },

    /**
     * Delete participant
     */
    async deleteParticipant(participantId) {
        const content = `
            <p>¿Estás seguro de que deseas eliminar este participante?</p>
            <p class="text-muted">Esta acción no se puede deshacer.</p>
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
                onclick: `Participants.confirmDelete(${participantId})`
            }
        ]);
    },

    /**
     * Confirm delete participant
     */
    async confirmDelete(participantId) {
        try {
            await api.delete(API_ENDPOINTS.PARTICIPANT_DETAIL(participantId));

            UI.closeModal();
            UI.showToast('Participante eliminado exitosamente', 'success');

            // Reload participants
            if (Workshops.currentWorkshop) {
                await this.loadParticipants(Workshops.currentWorkshop.id);
                // Refresh workshop detail to update count
                await Workshops.viewWorkshop(Workshops.currentWorkshop.id);
            }
        } catch (error) {
            UI.showToast(`Error al eliminar participante: ${error.message}`, 'error');
        }
    }
};
