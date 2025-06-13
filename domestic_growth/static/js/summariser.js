;(function () {
    const form = document.querySelector('#summary_feedback_form')
    const formContainer = document.querySelector("#summariser_feedback_form_container")
    const firstStageOptions = form.querySelectorAll('label[name="was_useful"]');
    const secondStageContainer = form.querySelector('#id_feedback_text_container');
    const submitButton = form.querySelector("#feedback_submit");
    
    secondStageContainer.classList.add('great-hidden');
    submitButton.classList.add('great-hidden');

    for (var i = 0 ; i < firstStageOptions.length; i++) {
        firstStageOptions[i].addEventListener(('click'), () => {
            secondStageContainer.classList.remove('great-hidden');
            submitButton.classList.remove('great-hidden');
        })
    }

    const showSuccessMessage = () => {
        const successContainer = document.querySelector('#feedback_success_container')
        successContainer.classList.remove('great-hidden')
        formContainer.classList.add('great-hidden');
        
    }
    form.addEventListener(('submit'), async (event) => {
        event.preventDefault()

        const formData = new FormData(form);
        const url = form.action
        formData.append('js_enabled', "true");

        try {
                const response = await fetch(`${url}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                });

                if (response.status==200) {
                    showSuccessMessage()
                }
            } catch (error) {
                const errors = await response.json();
                console.error('There was a problem with the fetch operation:', error);
            }
    })
})()