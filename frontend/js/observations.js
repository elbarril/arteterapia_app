// Observations Module
const Observations = {
    currentObservationData: null,
    currentQuestionIndex: 0,
    questions: [],
    answerOptions: [],
    sessionId: null,
    participantId: null,
    workshopId: null,

    /**
     * Get all observations for a workshop
     */
    async getWorkshopObservations(workshopId) {
        try {
            return await api.get(API_ENDPOINTS.WORKSHOP_OBSERVATIONS(workshopId));
        } catch (error) {
            UI.showToast(`Error loading observations: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Get single observation
     */
    async getObservation(observationId) {
        try {
            return await api.get(API_ENDPOINTS.OBSERVATION_DETAIL(observationId));
        } catch (error) {
            UI.showToast(`Error loading observation: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Get all questions
     */
    async getQuestions() {
        try {
            const data = await api.get(API_ENDPOINTS.OBSERVATION_QUESTIONS);
            this.questions = data.questions;
            this.answerOptions = data.answer_options;
            return data;
        } catch (error) {
            UI.showToast(`Error loading questions: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Initialize observation
     */
    async initializeObservation(sessionId, participantId) {
        try {
            const data = await api.post(API_ENDPOINTS.OBSERVATION_INITIALIZE, {
                session_id: sessionId,
                participant_id: participantId
            });

            this.currentObservationData = data.observation_data;
            this.currentQuestionIndex = 0;

            return data;
        } catch (error) {
            UI.showToast(`Error initializing observation: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Save observation
     */
    async saveObservation(freeformNotes = '') {
        try {
            const result = await api.post(API_ENDPOINTS.OBSERVATION_SAVE, {
                observation_data: this.currentObservationData,
                freeform_notes: freeformNotes
            });

            UI.showToast('Observation saved successfully', 'success');
            this.currentObservationData = null;
            this.currentQuestionIndex = 0;
            return result;
        } catch (error) {
            UI.showToast(`Error saving observation: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Delete observation
     */
    async deleteObservation(observationId) {
        try {
            const result = await api.delete(API_ENDPOINTS.OBSERVATION_DETAIL(observationId));
            UI.showToast('Observation deleted successfully', 'success');
            return result;
        } catch (error) {
            UI.showToast(`Error deleting observation: ${error.message}`, 'error');
            throw error;
        }
    },

    /**
     * Start observation workflow
     */
    async startObservation(sessionId, participantId, workshopId) {
        try {
            this.sessionId = sessionId;
            this.participantId = participantId;
            this.workshopId = workshopId;

            // Load questions if not already loaded
            if (this.questions.length === 0) {
                await this.getQuestions();
            }

            // Initialize observation
            const data = await this.initializeObservation(sessionId, participantId);

            // Show observation page
            UI.showPage('observationPage');

            // Render first question
            this.renderQuestion(0);

            // Setup event listeners
            this.setupEventListeners();
        } catch (error) {
            console.error('Error starting observation:', error);
        }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Cancel button
        const cancelBtn = document.getElementById('cancelObservationBtn');
        if (cancelBtn) {
            cancelBtn.onclick = () => this.cancelObservation();
        }

        // Previous button
        const prevBtn = document.getElementById('prevQuestionBtn');
        if (prevBtn) {
            prevBtn.onclick = () => this.previousQuestion();
        }

        // Next button
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (nextBtn) {
            nextBtn.onclick = () => this.nextQuestion();
        }

        // Finish button
        const finishBtn = document.getElementById('finishObservationBtn');
        if (finishBtn) {
            finishBtn.onclick = () => this.finishObservation();
        }
    },

    /**
     * Render question
     */
    renderQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;

        this.currentQuestionIndex = index;
        const question = this.questions[index];

        // Update progress
        const progress = ((index + 1) / this.questions.length) * 100;
        document.getElementById('observationProgress').style.width = `${progress}%`;
        document.getElementById('observationProgressText').textContent =
            `Pregunta ${index + 1} de ${this.questions.length}`;

        // Update category
        document.getElementById('observationCategory').textContent = question.category;

        // Update question text
        document.getElementById('observationQuestion').textContent = question.text;

        // Render answer buttons
        const answersContainer = document.getElementById('observationAnswers');
        const currentAnswer = this.currentObservationData.answers[question.id];

        // Answer option labels in Spanish
        const answerLabels = {
            'yes': 'Sí',
            'no': 'No',
            'partially': 'Parcialmente',
            'not_applicable': 'No Aplica'
        };

        answersContainer.innerHTML = this.answerOptions.map(option => `
            <button class="answer-btn ${currentAnswer === option ? 'selected' : ''}" 
                    data-answer="${option}"
                    onclick="Observations.selectAnswer('${question.id}', '${option}')">
                ${answerLabels[option] || option}
            </button>
        `).join('');

        // Update navigation buttons
        document.getElementById('prevQuestionBtn').disabled = index === 0;
        document.getElementById('nextQuestionBtn').disabled = !currentAnswer;

        // Show/hide finish button
        const isLastQuestion = index === this.questions.length - 1;
        document.getElementById('nextQuestionBtn').style.display = isLastQuestion ? 'none' : 'flex';
        document.getElementById('finishObservationBtn').style.display = isLastQuestion && currentAnswer ? 'flex' : 'none';

        // Add animation
        const card = document.getElementById('observationPage').querySelector('.observation-card');
        card.classList.add('animating');
        setTimeout(() => card.classList.remove('animating'), 200);
    },

    /**
     * Select answer
     */
    selectAnswer(questionId, answer) {
        // Update answer in observation data
        this.currentObservationData.answers[questionId] = answer;

        // Update UI
        const buttons = document.querySelectorAll('.answer-btn');
        buttons.forEach(btn => {
            if (btn.dataset.answer === answer) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });

        // Enable next button
        document.getElementById('nextQuestionBtn').disabled = false;

        // If last question, show finish button
        const isLastQuestion = this.currentQuestionIndex === this.questions.length - 1;
        if (isLastQuestion) {
            document.getElementById('finishObservationBtn').style.display = 'flex';
        }
    },

    /**
     * Previous question
     */
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.renderQuestion(this.currentQuestionIndex - 1);
        }
    },

    /**
     * Next question
     */
    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.renderQuestion(this.currentQuestionIndex + 1);
        }
    },

    /**
     * Finish observation
     */
    async finishObservation() {
        // Show notes section
        document.getElementById('observationNotesSection').style.display = 'block';
        document.getElementById('finishObservationBtn').textContent = 'Guardar Observación';
        document.getElementById('finishObservationBtn').onclick = () => this.saveAndComplete();

        // Scroll to notes
        document.getElementById('observationNotesSection').scrollIntoView({ behavior: 'smooth' });
    },

    /**
     * Save and complete
     */
    async saveAndComplete() {
        const notes = document.getElementById('observationNotes').value.trim();

        try {
            await this.saveObservation(notes);

            // Go back to workshop detail
            if (this.workshopId) {
                await Workshops.viewWorkshop(this.workshopId);
            } else {
                UI.showPage('workshopsPage');
                await Workshops.loadWorkshops();
            }
        } catch (error) {
            console.error('Error saving observation:', error);
        }
    },

    /**
     * Cancel observation
     */
    cancelObservation() {
        if (confirm('¿Estás seguro de que deseas cancelar? Se perderá el progreso actual.')) {
            this.currentObservationData = null;
            this.currentQuestionIndex = 0;

            // Go back to workshop detail
            if (this.workshopId) {
                Workshops.viewWorkshop(this.workshopId);
            } else {
                UI.showPage('workshopsPage');
                Workshops.loadWorkshops();
            }
        }
    },

    /**
     * Render observations list
     */
    renderObservationsList(observations, workshopId) {
        const container = document.getElementById('observations-list');
        if (!container) return;

        if (!observations || observations.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    No observations found.
                </div>
            `;
            return;
        }

        const html = observations.map(obs => `
            <div class="card mb-3" data-observation-id="${obs.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="card-title">
                                Session ${obs.session_id} - Participant ${obs.participant_id}
                                <span class="badge bg-primary ms-2">v${obs.version}</span>
                            </h6>
                            <p class="card-text">
                                <small class="text-muted">
                                    <i class="bi bi-calendar me-1"></i>
                                    ${new Date(obs.created_at).toLocaleString()}
                                </small>
                            </p>
                            ${obs.freeform_notes ? `
                                <p class="card-text">
                                    <small><strong>Notes:</strong> ${this.escapeHtml(obs.freeform_notes)}</small>
                                </p>
                            ` : ''}
                            <p class="card-text">
                                <small class="text-muted">
                                    ${Object.keys(obs.answers).length} questions answered
                                </small>
                            </p>
                        </div>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="Observations.viewObservation(${obs.id})">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="Observations.confirmDeleteObservation(${obs.id}, ${workshopId})">
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
     * View observation details
     */
    async viewObservation(observationId) {
        try {
            const observation = await this.getObservation(observationId);

            // Show modal with observation details
            const content = `
                <div class="mb-3">
                    <strong>Session:</strong> ${observation.session_id}<br>
                    <strong>Participant:</strong> ${observation.participant_id}<br>
                    <strong>Version:</strong> ${observation.version}<br>
                    <strong>Created:</strong> ${new Date(observation.created_at).toLocaleString()}
                </div>
                ${observation.freeform_notes ? `
                    <div class="mb-3">
                        <strong>Notes:</strong><br>
                        ${this.escapeHtml(observation.freeform_notes)}
                    </div>
                ` : ''}
                <div class="mb-3">
                    <strong>Answers:</strong><br>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Question</th>
                                    <th>Answer</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(observation.answers).map(([q, a]) => `
                                    <tr>
                                        <td>${this.escapeHtml(q)}</td>
                                        <td><span class="badge bg-secondary">${this.escapeHtml(a)}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            UI.showModal('Observation Details', content, [
                {
                    text: 'Close',
                    class: 'btn-outline',
                    onclick: 'UI.closeModal()'
                }
            ]);
        } catch (error) {
            console.error('Error viewing observation:', error);
        }
    },

    /**
     * Confirm delete observation
     */
    confirmDeleteObservation(observationId, workshopId) {
        if (confirm('Are you sure you want to delete this observation? This action cannot be undone.')) {
            this.deleteObservationAndRefresh(observationId, workshopId);
        }
    },

    /**
     * Delete observation and refresh list
     */
    async deleteObservationAndRefresh(observationId, workshopId) {
        try {
            await this.deleteObservation(observationId);
            const observations = await this.getWorkshopObservations(workshopId);
            this.renderObservationsList(observations, workshopId);
        } catch (error) {
            console.error('Error deleting observation:', error);
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
