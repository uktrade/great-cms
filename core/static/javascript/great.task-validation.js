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
          const message = document.getElementById('task-validation-message')

          const titles = [
            {
              title: 'Understand how to classify your products',
              question:
                'You want to learn more about how to classify your goods for export?',
              message:
                "You're being redirected to an article from Learn to Export.",
            },
            {
              title: 'Get the right commodity code',
              question:
                'You need to find the correct commodity (HS) code to export your goods?',
            },
            {
              title: 'Make a simplified customs declaration',
              question:
                'You want to make a simplified customs declaration using our online service?',
            },
            {
              title: 'Find a customs agent or fast parcel operator',
              question:
                'You are looking for a list of customs agents or fast parcel operators you can contact?',
            },
            {
              title: 'Claim with Returned Goods Relief (RGR)',
              question:
                "You want to claim for returned goods relief on goods you've re-imported into the UK?",
            },
          ]

          titles.forEach((obj) => {
            if (title === obj.title) {
              question.innerHTML = obj.question

              if (obj.message) {
                message.innerHTML = obj.message
              }
            }
          })

          if (sessionStorage.getItem('task_validation')) {
            ga('service', title, 'main-area')
            redirectUserToCardHref(href)
          } else {
            sessionStorage.setItem('task_validation', 'true')

            if (form) {
              GreatFrontend.utils.showElement(form)

              form.querySelectorAll('[data-modal-submit]').forEach((button) => {
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
