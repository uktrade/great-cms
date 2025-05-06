;(function () {
  const hasUserConsentedToTracking = () => {
    let hasUserConsented = false
    const cookiesArray = document.cookie.split('; ')

    cookiesArray.forEach((cookieString) => {
      if (
        cookieString.includes('cookies_policy') &&
        cookieString.includes('"usage":true')
      ) {
        hasUserConsented = true
      }
    })

    return hasUserConsented
  }

  const customTracking = () => {
    const ga_items = document.querySelectorAll(
      'a[data-ga-digital-entry-point], div[data-ga-digital-entry-point] a'
    )
    const has_ga_items = ga_items.length >= 1
    const values = ['category', 'title', 'location']

    if (has_ga_items) {
      ga_items.forEach((item) => {
        item.addEventListener('click', (e) => {
          e.preventDefault()

          let data = {}
          const isNestedAnchor = item.parentElement.dataset.hasOwnProperty(
            'gaDigitalEntryPoint'
          )

          values.forEach((value) => {
            let el

            if (isNestedAnchor) {
              el = item.parentElement.querySelector(`[data-${value}]`)
            } else {
              el = item.querySelector(`[data-${value}]`)
            }

            if (el) {
              data[value] = el.dataset[value]
            }
          })

          if (window.dataLayer) {
            window.dataLayer.push({
              event: 'DEPCardClick',
              category: data.category,
              title: data.title,
              location: data.location,
            })
          }

          if (localStorage.getItem('dep_triage_journey')) {
            localStorage.setItem(
              'dep_triage_journey',
              `${localStorage.getItem('dep_triage_journey')} > ${data.title}`
            )
          } else {
            localStorage.setItem('dep_triage_journey', `${data.title}`)
          }

          window.location = item.href
        })
      })

      if (
        window.location.pathname.includes('/support/export-support/') ||
        window.location.pathname.includes('/export-from-uk/support-topics/')
      ) {
        if (localStorage.getItem('dep_triage_journey')) {
          localStorage.setItem(
            'dep_triage_journey',
            `${localStorage.getItem(
              'dep_triage_journey'
            )} > Support landing page`
          )
        } else {
          localStorage.setItem('dep_triage_journey', 'Support landing page')
        }
      }
    }
  }

  if (!hasUserConsentedToTracking()) return

  customTracking()
})()
