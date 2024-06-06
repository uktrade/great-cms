class CsatFormHandler {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.stepOne = document.getElementById('csat-step-1');
        this.stepTwo = document.getElementById('csat-step-2');
        this.stepOneSuccessMessage = document.getElementById('csat-step-1-submission-confirmation');
        this.stepTwoSuccessMessage = document.getElementById('csat-step-2-submission-confirmation');
        this.infoMsg = document.getElementById('info-message')
        this.errorSummary = document.getElementById('error-summary');
        this.errorSummaryTitle = this.errorSummary.querySelector('.govuk-error-summary__title');
        this.errorList = this.errorSummary.querySelector('.govuk-error-summary__list');
        this.submitButton = this.form.querySelectorAll('button[type="submit"]')[0];
        this.cancelButton = this.form.querySelectorAll('button[type="submit"]')[1];
        this.currentStep = 1;
        this.hideClass = 'great-hidden';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(this.form);
            formData.append('step', this.currentStep);
            const url = this.form.action
            
            if (event.submitter && event.submitter.name=='cancelButton'){
                this.resetForm();
                return
            }

            try {
                const response = await fetch(`${url}?js_enabled=True`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                });

                const data = await response.json();
                this.handleStepTransition(response, data);
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
                this.showErrors();
            }
        });
    }

    resetForm() {
        this.stepTransition(this.stepTwo, this.stepOne, this.stepTwoSuccessMessage, '');
        this.form.classList.add(this.hideClass);
        this.infoMsg.classList.add(this.hideClass);
        this.stepOneSuccessMessage.classList.add(this.hideClass);
        this.currentStep = 1;
    }

    handleStepTransition(response, data) {
        this.clearExistingErrors(data);
        if (response.status==200) {
            if (this.currentStep === 1) {
                this.infoMsg.classList.remove(this.hideClass);
                this.cancelButton.classList.remove('great-hidden');
                this.stepTransition(this.stepOne, this.stepTwo, this.stepOneSuccessMessage, 'Submit feedback');
                this.currentStep = 2;
            } else {
                this.stepTransition(this.stepTwo, this.stepOne, this.stepTwoSuccessMessage, '');
                this.form.classList.add(this.hideClass);
                this.stepOneSuccessMessage.classList.add(this.hideClass);

                this.infoMsg.classList.add(this.hideClass);
                this.currentStep=1;
            }
        } else if (data) {
            this.showErrors(data);
        }
    }

    stepTransition(hideStep, showStep, showMessage, buttonLabel) {
        hideStep.classList.add(this.hideClass);
        if (showStep) {
            showStep.classList.remove(this.hideClass);
        }
        showMessage.classList.remove(this.hideClass);
        showMessage.focus();
        this.errorSummary.classList.add(this.hideClass);
        if (buttonLabel) {
            this.submitButton.textContent = buttonLabel;
        }
    }
    
    showErrors(errors) {
        this.stepOneSuccessMessage.classList.add(this.hideClass);
        this.stepTwoSuccessMessage.classList.add(this.hideClass);

        if (!errors) {
            this.errorSummaryTitle.textContent = 'There is a problem with the network. Please try again.';
        } else {
            this.errorList.innerHTML = '';
            Object.keys(errors).forEach(field => {
                const fieldGroup = document.getElementById(field + '_group');
                if (fieldGroup) {
                    fieldGroup.classList.add('govuk-form-group--error');
                    const inlineError = fieldGroup.querySelector('.govuk-error-message');
                    if (inlineError) {
                        inlineError.classList.remove(this.hideClass);
                    }
                }

                errors[field].forEach(error => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<a href="#id_${field}">${error}</a>`;
                    this.errorList.appendChild(listItem);
                });
            });
        }
        this.errorSummary.classList.remove(this.hideClass);
        this.errorSummary.focus();
    }

    clearExistingErrors(hasErrors) {
        const errorFields = document.querySelectorAll('.govuk-form-group--error');
        errorFields.forEach(fieldGroup => {
            const fieldName = fieldGroup.id.replace('_group', '');
    
            if (!hasErrors[fieldName]) {
                this.removeErrorClasses(fieldGroup);
            }
        });
    }

    removeErrorClasses(fieldGroup) {
        if (fieldGroup) {
            fieldGroup.classList.remove('govuk-form-group--error');
            const inlineError = fieldGroup.querySelector('.govuk-error-message');
            if (inlineError) {
                inlineError.classList.add(this.hideClass);
            }
        }
    }
}
