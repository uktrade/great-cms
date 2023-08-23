const feedbackButton = document.getElementById('feedback_button')

const toggleButtonTextContainer = () => {
  const text = document.getElementById('feedback-text')
  const feedbackContainer = document.getElementById('feedback_container')
  feedbackButton.classList.toggle('great-hidden')
  text.classList.toggle('great-hidden')
  feedbackContainer.classList.toggle('great-box-shadow')
  return
}

feedbackButton.addEventListener('click', toggleButtonTextContainer)

document
  .getElementById('no_thanks')
  .addEventListener('click', toggleButtonTextContainer)
