/**
 * Observation Flow Manager
 * Handles the step-by-step observation recording process
 */

class ObservationFlow {
    constructor(config) {
        this.currentQuestionId = config.currentQuestionId;
        this.currentIndex = config.currentIndex;
        this.totalQuestions = config.totalQuestions;
        this.previousAnswers = config.previousAnswers;
        this.isRedo = config.isRedo;

        this.init();
    }

    init() {
        // Highlight previous answer if exists
        this.highlightPreviousAnswer();

        // Event delegation for answer buttons
        document.addEventListener('click', (e) => {
            const answerBtn = e.target.closest('[data-action="submit-answer"]');
            if (answerBtn) {
                const answer = answerBtn.dataset.answerValue;
                this.submitAnswer(answer);
            }
        });

        // Complete observation button
        const completeBtn = document.querySelector('[data-action="complete-observation"]');
        if (completeBtn) {
            completeBtn.addEventListener('click', () => this.complete());
        }
    }

    highlightPreviousAnswer() {
        const previousAnswer = this.previousAnswers[this.currentQuestionId];
        if (previousAnswer) {
            const answerBtn = document.querySelector(`[data-answer-value="${previousAnswer}"]`);
            if (answerBtn) {
                answerBtn.classList.add('previously-answered');
            }
        }
    }

    async submitAnswer(answer) {
        // Disable buttons during submission
        const buttons = document.querySelectorAll('.answer-btn');
        buttons.forEach(btn => btn.disabled = true);

        try {
            const data = await apiClient.post('/observation/process-answer', {
                question_id: this.currentQuestionId,
                answer: answer
            });

            if (data.success) {
                if (data.has_more) {
                    // Update to next question
                    this.updateQuestion(data);
                } else {
                    // Show notes card
                    document.getElementById('questionCard').classList.add('d-none');
                    document.getElementById('notesCard').classList.remove('d-none');
                }
            } else {
                await modalManager.alert(data.message || 'Error al procesar respuesta');
                buttons.forEach(btn => btn.disabled = false);
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
            buttons.forEach(btn => btn.disabled = false);
        }
    }

    updateQuestion(data) {
        // Update current question data
        this.currentQuestionId = data.next_question.id;
        this.currentIndex = data.question_index;

        // Update question text
        document.getElementById('questionText').textContent = data.next_question.text;
        document.getElementById('currentQuestion').textContent = this.currentIndex + 1;

        // Update category
        let categoryHTML = `<small class="text-muted text-uppercase fw-bold">${data.next_question.category}</small>`;
        if (data.next_question.subcategory) {
            categoryHTML += `<br><small class="text-muted">${data.next_question.subcategory}</small>`;
        }
        document.getElementById('questionCategory').innerHTML = categoryHTML;

        // Update progress
        const progress = ((this.currentIndex + 1) / this.totalQuestions * 100);
        document.getElementById('observationProgress').style.width = progress + '%';

        // Remove previous highlighting and re-enable buttons
        const buttons = document.querySelectorAll('.answer-btn');
        buttons.forEach(btn => {
            btn.classList.remove('previously-answered');
            btn.disabled = false;
        });

        // Highlight if this question was previously answered
        this.highlightPreviousAnswer();
    }

    async complete() {
        const notes = document.getElementById('freeformNotes').value;

        try {
            const data = await apiClient.post('/observation/complete', {
                freeform_notes: notes
            });

            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                await modalManager.alert(data.message || 'Error al guardar');
            }
        } catch (error) {
            console.error('Error:', error);
            await modalManager.alert('Error de conexión');
        }
    }
}
