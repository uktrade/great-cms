GreatFrontend = window.GreatFrontend || {}

GreatFrontend.DynamicDropDowns = {
  init: (trigger_value, ignore_values = []) => {
    const level_1_dropdown = document.getElementById('id_enquiry_subject')
    const level_2_dropdown = document.getElementById('enquiry_subject_level_2')
    const level_2_select = document.getElementById('id_enquiry_subject_level_2')
    const level_3_checkboxes = document.getElementById(
      'enquiry_subject_level_3'
    )

    GreatFrontend.utils.hideElement(level_2_dropdown)
    GreatFrontend.utils.hideElement(level_3_checkboxes)

    if (level_1_dropdown.value === trigger_value) {
      GreatFrontend.utils.showElement(level_2_dropdown)

      if (!ignore_values.includes(level_2_select.value)) {
        GreatFrontend.utils.showElement(level_3_checkboxes)

        document.querySelectorAll('[data-value]').forEach((el) => {
          if (el.dataset.value.includes(level_2_select.value)) {
            GreatFrontend.utils.showElement(el)
          } else {
            GreatFrontend.utils.hideElement(el)
          }
        })
      }
    }

    level_1_dropdown.addEventListener('change', (e) => {
      if (e.target.value === trigger_value) {
        GreatFrontend.utils.showElement(level_2_dropdown)
      } else {
        GreatFrontend.utils.hideElement(level_2_dropdown)
        GreatFrontend.utils.hideElement(level_3_checkboxes)
      }
    })

    level_2_select.addEventListener('change', (e) => {
      if (ignore_values.includes(e.target.value)) {
        GreatFrontend.utils.hideElement(level_3_checkboxes)
      } else {
        GreatFrontend.utils.showElement(level_3_checkboxes)

        document.querySelectorAll('[data-value]').forEach((el) => {
          if (el.dataset.value.includes(e.target.value)) {
            GreatFrontend.utils.showElement(el)
          } else {
            GreatFrontend.utils.hideElement(el)
          }

          el.querySelector('input').checked = false
        })
      }
    })
  },
}
