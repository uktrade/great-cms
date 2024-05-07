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
              "You need to figure out the amount of duty to pay on the goods you're exporting."
          }

          if (title === 'Find the right commodity code') {
            question.innerHTML =
              'You need to find the correct commodity (HS) code to export your goods.'
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

                  const csrfToken = document.querySelector(
                    '[name=csrfmiddlewaretoken]'
                  ).value

                  try {
                    await fetch('/contact/task-validation', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                      },
                      body: JSON.stringify({
                        question: question.innerHTML,
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
