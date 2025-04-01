class CsatFormHandler {

    constructor(formId, csat_complete_key='csat_complete') {
        this.form = document.getElementById(formId);
        this.stepOne = document.querySelectorAll('.csat-step-1');
        this.stepTwo = document.querySelectorAll('.csat-step-2');
        this.stepOneSuccessMessage = document.getElementById('csat-step-1-submission-confirmation');
        this.stepTwoSuccessMessage = document.getElementById('csat-step-2-submission-confirmation');
        this.infoMsg = document.getElementById('info-message')
        this.errorSummary = document.getElementById('hcsat_error');
        this.errorSummaryTitle = this.errorSummary.querySelector('.govuk-error-summary__title');
        this.errorList = this.errorSummary.querySelector('.govuk-error-summary__list');
        this.submitButton = this.form.querySelectorAll('input[type="submit"]')[0];
        this.cancelButton = this.form.querySelectorAll('input[type="submit"]')[1];
        this.currentStep = 1;
        this.hideClass = 'great-hidden';
        this.csat_complete_key = csat_complete_key;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(this.form);
            formData.append('step', this.currentStep);
            const url = this.form.action.split('#')[0] // remove hash at the end so js_enabled arg isn't ignored

            let cancelButtonPressed = false
            if (event.submitter && event.submitter.name == 'cancelButton'){
                cancelButtonPressed = true
                formData.append('cancelButton',true)
                this.resetForm();
            }
            try {
                const response = await fetch(`${url}?js_enabled=True`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                });
                if (!cancelButtonPressed){
                    const data = await response.json();
                    this.handleStepTransition(response, data);
                }
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
                sessionStorage.setItem(this.csat_complete_key, 'true')
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
        hideStep.forEach(group => {
            console.log(group)
            group.classList.add(this.hideClass);
        });
        if (showStep) {
            showStep.forEach(group => {
                group.classList.remove(this.hideClass);
            });
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
