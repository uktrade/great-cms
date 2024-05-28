class CsatFormHandler {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.stepOne = document.getElementById('csat-step-1');
        this.stepTwo = document.getElementById('csat-step-2');
        this.stepOneSuccessMessage = document.getElementById('csat-step-1-submission-confirmation');
        this.stepTwoSuccessMessage = document.getElementById('csat-step-2-submission-confirmation');
        this.errorSummary = document.getElementById('error-summary');
        this.errorSummaryTitle = this.errorSummary.querySelector('.govuk-error-summary__title');
        this.errorList = this.errorSummary.querySelector('.govuk-error-summary__list');
        this.submitButton = this.form.querySelector('button[type="submit"]');
        this.currentStep = 1;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(this.form);
            formData.append('step', this.currentStep);

            try {
                const response = await this.simulateFetch('/some-endpoint/', { //simulateFetch - change to fetch when endpoint ready and update url
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                });

                const data = await response.json();
                this.handleStepTransition(data);
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
                this.showErrorSummary();
            }
        });
    }

    handleStepTransition(data) {
        this.checkExistingErrors();
        if (data.success) {
            if (this.currentStep === 1) {
                this.stepTransition(this.stepOne, this.stepTwo, this.stepOneSuccessMessage, 'Submit feedback');
                this.currentStep = 2;
            } else {
                this.stepTransition(this.stepTwo, null, this.stepTwoSuccessMessage, '');
                this.form.classList.add('great-hidden');
                this.stepOneSuccessMessage.classList.add('great-hidden');
            }
        } else if (data.errors) {
            this.showErrorSummary(data.errors);
        }
    }

    stepTransition(hideStep, showStep, showMessage, buttonLabel) {
        hideStep.classList.add('great-hidden');
        if (showStep) {
            showStep.classList.remove('great-hidden');
        }
        showMessage.classList.remove('great-hidden');
        showMessage.focus();
        this.errorSummary.classList.add('great-hidden');
        if (buttonLabel) {
            this.submitButton.textContent = buttonLabel;
        }
    }

    showErrorSummary(errors) {
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
                        inlineError.classList.remove('great-hidden');
                    }
                }

                errors[field].forEach(error => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<a href="#id_${field}">${error}</a>`;
                    this.errorList.appendChild(listItem);
                });
            });
        }
        this.errorSummary.classList.remove('great-hidden');
        this.errorSummary.focus();
    }

    checkExistingErrors() {
        const errorFields = document.querySelectorAll('.govuk-form-group--error');
        errorFields.forEach(fieldGroup => {
            const inputs = fieldGroup.querySelectorAll('input[type="checkbox"], input[type="radio"]');
            if (inputs.length) {
                const isChecked = Array.from(inputs).some(input => input.checked);
                if (isChecked) {
                    this.removeErrorClasses(fieldGroup);
                }
            }
        });
    }
    
    removeErrorClasses(fieldGroup) {
        if (fieldGroup) {
            fieldGroup.classList.remove('govuk-form-group--error');
            const inlineError = fieldGroup.querySelector('.govuk-error-message');
            if (inlineError) {
                inlineError.classList.add('great-hidden');
            }
        }
    }

    //////////////////////////////////////////////////////////////
    // Simulate fetch for testing - ***to be removed***
    //////////////////////////////////////////////////////////////

    async simulateFetch(url, options) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        if (!options.body.get('satisfaction') && this.currentStep === 1) {
            let errors = {};
            errors.satisfaction = ['Select a satisfaction rating'];
            return new Response(JSON.stringify({ errors }), {
                status: 400,
                headers: { 'Content-type': 'application/json' }
            });
        } else if (this.currentStep === 2 && (!options.body.get('experience') || !options.body.get('likelihood_of_return'))) {
            let errors = {};
            if (!options.body.get('experience')) {
                errors.experience = ['Select one or more issues'];
            }
            if (!options.body.get('likelihood_of_return')) {
                errors.likelihood_of_return = ['Select one likelihood of returning option'];
            }
            return new Response(JSON.stringify({ errors }), {
                status: 400,
                headers: { 'Content-type': 'application/json' }
            });
        } else {
            return new Response(JSON.stringify({ success: true }), {
                status: 200,
                headers: { 'Content-type': 'application/json' }
            });
        }
    }
}
