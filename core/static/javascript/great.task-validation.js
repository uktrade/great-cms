GreatFrontend = window.GreatFrontend || {}

GreatFrontend.TaskValidation = {
  init: () => {
    const cards = document.querySelectorAll('[data-task-validation]')
    const form = document.getElementById('task-validation-form')

    const ga = (category, title, location) => {
      window.dataLayer.push({
        event: 'DEPCardClick',
        category: category,
        title: title,
        location: location,
      })
    }

    const redirectUserToCardHref = (href) => {
      window.location = href
    }

    if (form) {
      GreatFrontend.utils.hideElement(form)
    }

    if (cards.length >= 1) {
      cards.forEach((card) => {
        card.addEventListener('click', async (e) => {
          e.preventDefault()

          const href = card.href

          const title = card.querySelector('[data-title]').dataset.title
          const question = document.getElementById('task-validation-question')

          if (title === 'Calculate how much duty you need to pay') {
            question.innerHTML =
              'We think you’re looking for the amount of duty you need to pay on your goods. Is this correct?'
          }

          if (title === 'Find the right commodity code') {
            question.innerHTML =
              'We think you’re looking for the correct commodity (HS) code for your product. Is this correct?'
          }

          if (sessionStorage.getItem('task_validation')) {
            ga('service', title, 'main-area')
            redirectUserToCardHref(href)
          } else {
            sessionStorage.setItem('task_validation', 'true')

            if (form) {
              GreatFrontend.utils.showElement(form)

              form.querySelectorAll('button').forEach((button) => {
                button.addEventListener('click', async (e) => {
                  e.preventDefault()

                  try {
                    await fetch('/contact/task-validation', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        question: question,
                        answer: button.innerText,
                      }),
                    })
                    ga('service', title, 'main-area')
                    redirectUserToCardHref(href)
                  } catch (e) {
                    console.log(e)
                  }
                })
              })
            }
          }
        })
      })
    }
  },
}
