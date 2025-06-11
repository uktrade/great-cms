;(function () {
    const form = document.getElementById('summariser_feedback_form')
    const secondStageContainer = form.querySelector('#id_feedback_text_container');
    const submitButton = form.querySelector("#feedback_submit");
    const firstStageOptions = form.querySelectorAll('label[name="was_useful"]');
    
    secondStageContainer.classList.add('great-hidden');
    submitButton.classList.add('great-hidden');

    for (var i = 0 ; i < firstStageOptions.length; i++) {
        firstStageOptions[i].addEventListener(('click'), () => {
            secondStageContainer.classList.remove('great-hidden');
            submitButton.classList.remove('great-hidden');
        })
    }
})()