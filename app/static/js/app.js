// Main JavaScript for Arteterapia Application
// Handles AJAX interactions for workshop detail view

// ===== Global Modal Helpers =====
const showModal = {
    alert: (message, title = 'Mensaje') => {
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
    },
    confirm: (message, title = 'Confirmación', confirmBtnText = 'Confirmar', confirmBtnClass = 'btn-danger') => {
        return new Promise((resolve) => {
            const modalEl = document.getElementById('globalConfirmModal');
            document.getElementById('globalConfirmTitle').textContent = title;
            document.getElementById('globalConfirmMessage').textContent = message;

            const confirmBtn = document.getElementById('globalConfirmBtn');
            confirmBtn.textContent = confirmBtnText;
            confirmBtn.className = `btn ${confirmBtnClass}`;

            const modal = new bootstrap.Modal(modalEl);
            let confirmed = false;

            // Remove existing listeners to prevent duplicates if instance persists
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
    },
    prompt: (label, defaultValue = '', title = 'Ingresar Datos') => {
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
};

// ===== Objective Management =====
function editObjective() {
    document.getElementById('objectiveDisplay').classList.add('d-none');
    document.getElementById('objectiveEdit').classList.remove('d-none');
    document.getElementById('objectiveText').focus();
}

function cancelEditObjective() {
    document.getElementById('objectiveDisplay').classList.remove('d-none');
    document.getElementById('objectiveEdit').classList.add('d-none');
}

function saveObjective() {
    const objective = document.getElementById('objectiveText').value;

    fetch(`/workshop/${workshopId}/objective`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ objective: objective })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const displayDiv = document.getElementById('objectiveDisplay');
                if (objective.trim()) {
                    displayDiv.innerHTML = `<p class="mb-0">${objective}</p>`;
                } else {
                    displayDiv.innerHTML = '<p class="text-muted fst-italic mb-0">Haga clic para agregar un objetivo...</p>';
                }
                cancelEditObjective();
            } else {
                showModal.alert('Error al actualizar objetivo');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

// ===== Participant Management =====
function showAddParticipant() {
    document.getElementById('addParticipantForm').classList.remove('d-none');
    document.getElementById('newParticipantName').focus();
}

function cancelAddParticipant() {
    document.getElementById('addParticipantForm').classList.add('d-none');
    document.getElementById('newParticipantName').value = '';
}

function createParticipant() {
    const name = document.getElementById('newParticipantName').value.trim();

    if (!name) {
        showModal.alert('El nombre es obligatorio');
        return;
    }

    fetch(`/workshop/${workshopId}/participant/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add participant to list
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item px-0 d-flex justify-content-between align-items-center';
                listItem.setAttribute('data-participant-id', data.participant.id);
                listItem.innerHTML = `
                <span class="participant-name">${data.participant.name}</span>
                <div>
                    <button class="btn btn-sm btn-link text-muted" onclick="editParticipant(${data.participant.id}, '${data.participant.name}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger" onclick="deleteParticipant(${data.participant.id})">
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

                cancelAddParticipant();
            } else {
                showModal.alert(data.message || 'Error al crear participante');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

async function editParticipant(id, currentName) {
    const newName = await showModal.prompt('Editar nombre del participante:', currentName);

    if (newName && newName.trim() !== currentName) {
        fetch(`/participant/${id}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newName.trim() })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const listItem = document.querySelector(`[data-participant-id="${id}"]`);
                    listItem.querySelector('.participant-name').textContent = data.participant.name;

                    // Update name in onclick attributes
                    const editBtn = listItem.querySelector('.btn-link:first-child');
                    editBtn.setAttribute('onclick', `editParticipant(${id}, '${data.participant.name}')`);
                } else {
                    showModal.alert(data.message || 'Error al actualizar');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showModal.alert('Error de conexión');
            });
    }
}

async function deleteParticipant(id) {
    const confirmed = await showModal.confirm('¿Eliminar este participante?');
    if (!confirmed) {
        return;
    }

    fetch(`/participant/${id}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
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
                showModal.alert(data.message || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

// ===== Session Management =====
function toggleSession(sessionId) {
    const sessionBody = document.getElementById(`session${sessionId}`);
    const bsCollapse = new bootstrap.Collapse(sessionBody, {
        toggle: true
    });
}

function createSession() {
    const prompt = document.getElementById('sessionPrompt').value.trim();
    const motivation = document.getElementById('sessionMotivation').value.trim();
    const materials = document.getElementById('sessionMaterials').value.trim();

    if (!prompt) {
        showModal.alert('La consigna es obligatoria');
        return;
    }

    fetch(`/workshop/${workshopId}/session/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: prompt,
            motivation: motivation,
            materials: materials
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to show new session
                location.reload();
            } else {
                showModal.alert(data.message || 'Error al crear sesión');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

function editSession(sessionId) {
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

function updateSession() {
    const sessionId = document.getElementById('editSessionId').value;
    const prompt = document.getElementById('editSessionPrompt').value.trim();
    const motivation = document.getElementById('editSessionMotivation').value.trim();
    const materials = document.getElementById('editSessionMaterials').value.trim();

    if (!prompt) {
        showModal.alert('La consigna es obligatoria');
        return;
    }

    fetch(`/session/${sessionId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: prompt,
            motivation: motivation,
            materials: materials
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to show updated session
                location.reload();
            } else {
                showModal.alert(data.message || 'Error al actualizar sesión');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

async function deleteSession(sessionId) {
    const confirmed = await showModal.confirm('¿Eliminar esta sesión y todos sus registros?');
    if (!confirmed) {
        return;
    }

    fetch(`/session/${sessionId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove session from DOM
                const sessionCard = document.querySelector(`[data-session-id="${sessionId}"]`);
                sessionCard.remove();

                // Update count
                document.getElementById('sessionCount').textContent = data.session_count;
            } else {
                showModal.alert(data.message || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal.alert('Error de conexión');
        });
}

// ===== Enter key handling for forms =====
document.addEventListener('DOMContentLoaded', function () {
    // Add participant with Enter key
    const participantInput = document.getElementById('newParticipantName');
    if (participantInput) {
        participantInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                createParticipant();
            }
        });
    }
});
