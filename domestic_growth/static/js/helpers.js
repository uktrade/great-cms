;(function () {
  const emailInput = document.getElementById('id_email')
  const queryString = window.location.search

  if (emailInput && queryString.includes('resend_email=True')) {
    emailInput.focus()
  }

  const sectionNavButton = document.querySelector(
    '.bgs-service-navigation--guide button.govuk-service-navigation__toggle'
  )

  if (sectionNavButton) {
    sectionNavButton.click()
  }
})()
