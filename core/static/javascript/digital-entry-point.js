;(function () {
  const ga_items = document.querySelectorAll(
    'a[data-ga-digital-entry-point], div[data-ga-digital-entry-point] a'
  )
  const has_ga_items = ga_items.length >= 1
  const values = ['category', 'title', 'location']

  if (has_ga_items) {
    ga_items.forEach((item) => {
      item.addEventListener('click', (e) => {
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
      })
    })
  }
})()
