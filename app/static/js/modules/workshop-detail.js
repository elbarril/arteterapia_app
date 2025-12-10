/**
 * Workshop Detail Manager
 * Handles all interactions on the workshop detail page
 * Uses event delegation for dynamic content
 */

class WorkshopDetailManager {
    constructor(workshopId) {
        this.workshopId = workshopId;
        this.objectiveManager = new ObjectiveManager(workshopId);
        this.participantManager = new ParticipantManager(workshopId);
        this.sessionManager = new SessionManager(workshopId);

        this.init();
    }

    init() {
        this.objectiveManager.init();
        this.participantManager.init();
        this.sessionManager.init();
    }
}

/**
 * Objective Manager
 * Handles workshop objective editing
 */
class ObjectiveManager {
    constructor(workshopId) {
        this.workshopId = workshopId;
    }

    init() {
        // Event delegation for objective editing
        const objectiveDisplay = document.getElementById('objectiveDisplay');
        if (objectiveDisplay) {
            objectiveDisplay.addEventListener('click', () => this.edit());
        }

        const cancelBtn = document.querySelector('[data-action="cancel-objective"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelEdit());
        }

        const saveBtn = document.querySelector('[data-action="save-objective"]');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.save());
        }
    }

    edit() {
        document.getElementById('objectiveDisplay').classList.add('d-none');
        document.getElementById('objectiveEdit').classList.remove('d-none');
        document.getElementById('objectiveText').focus();
    }

    cancelEdit() {
        document.getElementById('objectiveDisplay').classList.remove('d-none');
        document.getElementById('objectiveEdit').classList.add('d-none');
    }

    async save() {
        const objective = document.getElementById('objectiveText').value;

        try {
            const data = await apiClient.post(`/workshop/${this.workshopId}/objective`, {
                objective: objective
            });

            if (data.success) {
                const displayDiv = document.getElementById('objectiveDisplay');
                if (objective.trim()) {
                    displayDiv.innerHTML = `<p class="mb-0">${objective}</p>`;
                } else {
                    displayDiv.innerHTML = '<p class="text-muted fst-italic mb-0">Haga clic para agregar un objetivo...</p>';
                }
                this.cancelEdit();
            } else {
                await modalManager.alert('Error al actualizar objetivo');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }
}

/**
 * Participant Manager
 * Handles participant CRUD operations
 */
class ParticipantManager {
    constructor(workshopId) {
        this.workshopId = workshopId;
    }

    init() {
        // Event delegation for participant actions
        const addBtn = document.querySelector('[data-action="show-add-participant"]');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddForm());
        }

        const cancelBtn = document.querySelector('[data-action="cancel-add-participant"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelAdd());
        }

        const createBtn = document.querySelector('[data-action="create-participant"]');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.create());
        }

        // Handle Enter key in participant input
        const participantInput = document.getElementById('newParticipantName');
        if (participantInput) {
            participantInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.create();
                }
            });
        }

        // Event delegation for edit/delete buttons
        document.addEventListener('click', (e) => {
            const editBtn = e.target.closest('[data-action="edit-participant"]');
            if (editBtn) {
                const id = editBtn.dataset.participantId;
                const name = editBtn.dataset.participantName;
                this.edit(id, name);
            }

            const deleteBtn = e.target.closest('[data-action="delete-participant"]');
            if (deleteBtn) {
                const id = deleteBtn.dataset.participantId;
                this.delete(id);
            }
        });
    }

    showAddForm() {
        document.getElementById('addParticipantForm').classList.remove('d-none');
        document.getElementById('newParticipantName').focus();
    }

    cancelAdd() {
        document.getElementById('addParticipantForm').classList.add('d-none');
        document.getElementById('newParticipantName').value = '';
    }

    async create() {
        const name = document.getElementById('newParticipantName').value.trim();

        if (!name) {
            await modalManager.alert('El nombre es obligatorio');
            return;
        }

        try {
            const data = await apiClient.post(`/workshop/${this.workshopId}/participant/create`, {
                name: name
            });

            if (data.success) {
                // Add participant to list
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item px-0 d-flex justify-content-between align-items-center';
                listItem.setAttribute('data-participant-id', data.participant.id);
                listItem.innerHTML = `
                    <span class="participant-name">${data.participant.name}</span>
                    <div>
                        <button class="btn btn-sm btn-link text-muted" 
                                data-action="edit-participant"
                                data-participant-id="${data.participant.id}"
                                data-participant-name="${data.participant.name}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-link text-danger"
                                data-action="delete-participant"
                                data-participant-id="${data.participant.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;

                const list = document.getElementById('participantsList');
                // Remove "no participants" message if exists
                const emptyMessage = list.querySelector('.fst-italic');
                if (emptyMessage) {
                    emptyMessage.remove();
                }
                list.appendChild(listItem);

                // Update count
                document.getElementById('participantCount').textContent = data.participant_count;

                this.cancelAdd();
            } else {
                await modalManager.alert(data.message || 'Error al crear participante');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }

    async edit(id, currentName) {
        const newName = await modalManager.prompt('Editar nombre del participante:', currentName);

        if (newName && newName.trim() !== currentName) {
            try {
                const data = await apiClient.post(`/participant/${id}/update`, {
                    name: newName.trim()
                });

                if (data.success) {
                    const listItem = document.querySelector(`[data-participant-id="${id}"]`);
                    listItem.querySelector('.participant-name').textContent = data.participant.name;

                    // Update data attributes
                    const editBtn = listItem.querySelector('[data-action="edit-participant"]');
                    editBtn.dataset.participantName = data.participant.name;
                } else {
                    await modalManager.alert(data.message || 'Error al actualizar');
                }
            } catch (error) {
                console.error('Error:', error);
                await modalManager.alert('Error de conexión');
            }
        }
    }

    async delete(id) {
        const confirmed = await modalManager.confirm('¿Eliminar este participante?');
        if (!confirmed) return;

        try {
            const data = await apiClient.post(`/participant/${id}/delete`);

            if (data.success) {
                const listItem = document.querySelector(`[data-participant-id="${id}"]`);
                listItem.remove();

                // Update count
                document.getElementById('participantCount').textContent = data.participant_count;

                // Add empty message if no more participants
                const list = document.getElementById('participantsList');
                if (list.children.length === 0) {
                    list.innerHTML = '<li class="list-group-item px-0 text-muted fst-italic">No hay participantes</li>';
                }
            } else {
                await modalManager.alert(data.message || 'Error al eliminar');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }
}

/**
 * Session Manager
 * Handles session CRUD operations and expand/collapse
 */
class SessionManager {
    constructor(workshopId) {
        this.workshopId = workshopId;
    }

    init() {
        // Event delegation for session actions
        document.addEventListener('click', (e) => {
            const toggleBtn = e.target.closest('[data-action="toggle-session"]');
            if (toggleBtn) {
                const sessionId = toggleBtn.dataset.sessionId;
                this.toggle(sessionId);
            }

            const editBtn = e.target.closest('[data-action="edit-session"]');
            if (editBtn) {
                const sessionId = editBtn.dataset.sessionId;
                this.edit(sessionId);
            }

            const deleteBtn = e.target.closest('[data-action="delete-session"]');
            if (deleteBtn) {
                const sessionId = deleteBtn.dataset.sessionId;
                this.delete(sessionId);
            }
        });

        // Create session button
        const createBtn = document.querySelector('[data-action="create-session"]');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.create());
        }

        // Update session button
        const updateBtn = document.querySelector('[data-action="update-session"]');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.update());
        }
    }

    toggle(sessionId) {
        const sessionBody = document.getElementById(`session${sessionId}`);
        const bsCollapse = new bootstrap.Collapse(sessionBody, {
            toggle: true
        });
    }

    async create() {
        const prompt = document.getElementById('sessionPrompt').value.trim();
        const motivation = document.getElementById('sessionMotivation').value.trim();
        const materials = document.getElementById('sessionMaterials').value.trim();

        if (!prompt) {
            await modalManager.alert('La consigna es obligatoria');
            return;
        }

        try {
            const data = await apiClient.post(`/workshop/${this.workshopId}/session/create`, {
                prompt: prompt,
                motivation: motivation,
                materials: materials
            });

            if (data.success) {
                // Reload page to show new session
                location.reload();
            } else {
                await modalManager.alert(data.message || 'Error al crear sesión');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }

    edit(sessionId) {
        // Get current session data from DOM
        const sessionCard = document.querySelector(`[data-session-id="${sessionId}"]`);
        const sessionBody = sessionCard.querySelector('.session-card-body');

        // Extract data
        const promptElement = sessionBody.querySelector('p:nth-child(1)');
        const prompt = promptElement.textContent.replace('Consigna: ', '');

        const motivationElement = sessionBody.querySelector('p:nth-child(2)');
        const motivation = motivationElement ? motivationElement.textContent.replace('Motivación: ', '') : '';

        const materialsElement = sessionBody.querySelector('p:nth-child(3)');
        const materials = materialsElement ? materialsElement.textContent.replace('Materiales: ', '') : '';

        // Populate edit modal
        document.getElementById('editSessionId').value = sessionId;
        document.getElementById('editSessionPrompt').value = prompt;
        document.getElementById('editSessionMotivation').value = motivation;
        document.getElementById('editSessionMaterials').value = materials;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('editSessionModal'));
        modal.show();
    }

    async update() {
        const sessionId = document.getElementById('editSessionId').value;
        const prompt = document.getElementById('editSessionPrompt').value.trim();
        const motivation = document.getElementById('editSessionMotivation').value.trim();
        const materials = document.getElementById('editSessionMaterials').value.trim();

        if (!prompt) {
            await modalManager.alert('La consigna es obligatoria');
            return;
        }

        try {
            const data = await apiClient.post(`/session/${sessionId}/update`, {
                prompt: prompt,
                motivation: motivation,
                materials: materials
            });

            if (data.success) {
                // Reload page to show updated session
                location.reload();
            } else {
                await modalManager.alert(data.message || 'Error al actualizar sesión');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }

    async delete(sessionId) {
        const confirmed = await modalManager.confirm('¿Eliminar esta sesión y todos sus registros?');
        if (!confirmed) return;

        try {
            const data = await apiClient.post(`/session/${sessionId}/delete`);

            if (data.success) {
                // Remove session from DOM
                const sessionCard = document.querySelector(`[data-session-id="${sessionId}"]`);
                sessionCard.remove();

                // Update count
                document.getElementById('sessionCount').textContent = data.session_count;
            } else {
                await modalManager.alert(data.message || 'Error al eliminar');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }
}
