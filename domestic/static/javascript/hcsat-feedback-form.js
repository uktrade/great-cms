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
            const url = this.form.action

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
                this.showErrorSummary();
            }
        });
    }

    handleStepTransition(response, data) {
        this.checkExistingErrors();
        if (response.status==200) {
            const infoMsg = document.getElementById('infoMessage')
            if (this.currentStep === 1) {
                infoMsg.classList.remove('great-hidden')
                this.stepTransition(this.stepOne, this.stepTwo, this.stepOneSuccessMessage, 'Submit feedback');
                this.currentStep = 2;
            } else {
                this.stepTransition(this.stepTwo, this.stepOne, this.stepTwoSuccessMessage, '');
                this.form.classList.add('great-hidden');
                this.stepOneSuccessMessage.classList.add('great-hidden');

                infoMsg.classList.add('great-hidden')
                this.currentStep=1
            }
        } else if (data) {
            this.showErrorSummary(data);
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
            this.stepOneSuccessMessage.classList.add('great-hidden');
            this.stepTwoSuccessMessage.classList.add('great-hidden');
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
                console.log(field)

                if (field == 'experience_other'){
                    const OtherField = document.getElementById('conditional-experience-4');
                    const errorField = OtherField.children[0]
                    console.log(OtherField)
                    console.log(OtherField.getElementsByClassName('govuk-error-message'))
                    if (OtherField.getElementsByClassName('govuk-error-message').length<1){
                        var inlineError = document.createElement("p");
                        inlineError.innerHTML='Enter the issue you experienced'
                        inlineError.classList.add('govuk-error-message')

                        errorField.insertBefore(inlineError,errorField.querySelector('#id_experience_other'))
                        errorField.classList.add('govuk-form-group--error');
                        console.log(errorField)
                    }

                }
                if (field == 'feedback_text'){
                    const errorGroup = document.getElementById('id_feedback_text')
                    console.log(errorGroup)
                    errorGroup.classList.add('govuk-form-group--error')
                    const errorField = document.getElementById('exceeding-characters-error');
                    errorField.classList.remove('great-hidden')
                }

                if (!Object.keys(errors).includes('feedback_text')){
                    const errorGroup = document.getElementById('id_feedback_text')
                    errorGroup.classList.remove('govuk-form-group--error')
                    const errorField = document.getElementById('exceeding-characters-error');
                    errorField.classList.add('great-hidden')
                }

                errors[field].forEach(error => {
                    const listItem = document.createElement('li');
                    if (field == 'feedback_text'){
                        listItem.innerHTML = `<a href="#with-hint">${'Your feedback must be 1200 characters or less'}</a>`;
                    }
                    else{
                    listItem.innerHTML = `<a href="#id_${field}">${error}</a>`;
                    }
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
}
