;(function () {
  const hidden_ta_trigger = document.querySelector('[data-hidden-ta-trigger]')
  const show_ta_trigger = document.querySelector('[data-show-ta-trigger]')

  if (hidden_ta_trigger && show_ta_trigger) {
    hidden_ta_trigger.addEventListener('click', (e) => {
      let focused_link = false

      document
        .querySelectorAll('[data-hidden-ta="true"]')
        .forEach((el, index) => {
          if (index == 0) {
            focused_link = el.querySelector('a')
          }

          if (index <= 4) {
            el.classList = ''
            el.dataset.hiddenTa = 'false'
          }
        })

      show_ta_trigger.classList =
        'govuk-!-margin-bottom-0 great-ds-button great-ds-button--secondary'

      if (focused_link) {
        focused_link.focus()
      }
    })

    show_ta_trigger.addEventListener('click', (e) => {
      document.querySelectorAll('[data-hidden-ta="false"]').forEach((el) => {
        el.classList = 'govuk-!-display-none'
        el.dataset.hiddenTa = 'true'
      })

      show_ta_trigger.classList = 'govuk-!-display-none'

      document.getElementById('trade-associations').scrollIntoView()

      if (hidden_ta_trigger) {
        hidden_ta_trigger.focus()
      }
    })

    show_ta_trigger.classList = 'govuk-!-display-none'
  }
})()
