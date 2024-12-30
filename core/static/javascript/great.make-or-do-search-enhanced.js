GreatFrontend = window.GreatFrontend || {}

GreatFrontend.MakeOrDoSearchEnhanced = {
  init: (sic_sector_data = {}, default_value = '') => {
    document.querySelector('#sic_description').remove()

    const sic_descriptions = sic_sector_data.data.map((el) => {
      const keywords = el.keywords ? '|' + el.keywords : ''
      return el.sic_description + keywords
    })
    accessibleAutocomplete({
      element: document.querySelector('#sic_description-container'),
      id: 'sic_description',
      name: 'sic_description',
      source: sic_descriptions,
      autoselect: false,
      minLength: 3,
      displayMenu: 'overlay',
      defaultValue: default_value,
      templates: {
        suggestion: (selectedSIC) => {
          const listbox = document.querySelector('#sic_description__listbox')

          if (listbox) {
            listbox.style.visibility = 'visible'
          }

          const search_input = document.querySelector('#sic_description')

          const match = sic_sector_data.data.find((el) => {
            return selectedSIC.includes(el.sic_description)
          })

          if (
            match &&
            match.sic_description &&
            match.dit_sector_list_field_04
          ) {
            let keywords = ''
            let keyword_parts = []

            if (match.keywords) {
              keywords = match.keywords
              keyword_parts = keywords
                .split(', ')
                .sort((a, b) => a.length - b.length)
            }

            if (search_input && keyword_parts) {
              let keyword_match = ''

              keyword_parts.some((keyword) => {
                if (
                  keyword
                    .toLowerCase()
                    .includes(search_input.value.toLowerCase())
                ) {
                  keyword_match = keyword
                  return true
                }
              })

              if (keyword_match) {
                return `<span>${match.sic_description} (${keyword_match})</span><br /><span class="govuk-body-s">${match.dit_sector_list_field_04}</span>`
              }
            }

            return `<span>${match.sic_description}</span><br /><span class="govuk-body-s">${match.dit_sector_list_field_04}</span>`
          }

          return '<span>No results found</span>'
        },
        inputValue: (selectedSIC = '') => {
          if (selectedSIC) {
            return selectedSIC.split('|')[0]
          }
        },
      },
      onConfirm: (selectedSIC) => {
        if (selectedSIC) {
          const {
            dit_sector_list_field_04,
            exporter_type = 'goods',
            keywords = null,
          } = sic_sector_data.data.find((el) =>
            selectedSIC.includes(el.sic_description)
          )
          const make_or_do_keyword = document.querySelector(
            '#make_or_do_keyword'
          )
          let is_keyword_match = false

          document.querySelector('#sector').value = dit_sector_list_field_04
          make_or_do_keyword.value = document
            .querySelector('#sic_description')
            .value.split('|')[0]
          document.querySelector('#exporter_type').value = exporter_type

          if (keywords) {
            is_keyword_match = keywords
              .toLowerCase()
              .includes(make_or_do_keyword.value.toLowerCase())

            let keyword_match = ''

            keyword_parts = keywords
              .split(', ')
              .sort((a, b) => a.length - b.length)

            keyword_parts.some((keyword) => {
              if (
                keyword
                  .toLowerCase()
                  .includes(make_or_do_keyword.value.toLowerCase())
              ) {
                keyword_match = keyword
                return true
              }
            })

            make_or_do_keyword.value = keyword_match
          }

          document.querySelector('#is_keyword_match').value = is_keyword_match
            ? 'True'
            : 'False'

          setTimeout(() => {
            if (is_keyword_match) {
              document.querySelector('#sic_description').value =
                document.querySelector('#sic_description').value +
                ' (' +
                make_or_do_keyword.value +
                ')'

              document.querySelector(
                '#sic_description__listbox'
              ).style.visibility = 'hidden'
            }
          }, 10)
        }
      },
      placeholder: 'For example, financial services or coffee roaster',
      inputClasses: 'govuk-input great-text-input great-ds-autocomplete-input',
      menuClasses: 'great-autocomplete-overlay',
      required: true,
    })

    const clear_search_button = document.querySelector('#clear_search')
    const sic_description = document.querySelector('#sic_description')
    const submit_button = document.querySelector(
      '[data-make-or-do-form] button[type="submit"]'
    )

    if (clear_search_button) {
      clear_search_button.addEventListener('click', (e) => {
        e.preventDefault()
        const selectors = [
          '#sector',
          '#make_or_do_keyword',
          '#exporter_type',
          '#sic_description',
        ]
        selectors.forEach(
          (selector) => (document.querySelector(selector).value = '')
        )

        clear_search_button.style.display = 'none'
      })

      clear_search_button.style.display = 'none'

      sic_description.addEventListener('focus', () => {
        clear_search_button.style.display = 'block'
      })

      sic_description.addEventListener('blur', () => {
        setTimeout(() => {
          clear_search_button.style.display = 'none'
        }, 200)
      })
    }

    if (submit_button) {
      submit_button.addEventListener('click', (e) => {
        e.preventDefault()

        const form = document.querySelector('[data-make-or-do-form]')
        const sector_hidden_input = document.querySelector(
          '[data-make-or-do-form] #sector'
        )
        const sic_description = document.querySelector(
          '[data-make-or-do-form] #sic_description'
        )
        const form_error_el = document.querySelector(
          '[data-make-or-do-form-error]'
        )

        const is_a_result_selected =
          sector_hidden_input && sector_hidden_input.value !== ''

        const is_sic_description_empty =
          sic_description && sic_description.value == ''

        const is_sic_description_unrecognised =
          sic_description &&
          sic_description.value !== '' &&
          sector_hidden_input &&
          sector_hidden_input.value == ''

        const is_sic_results_available = () => {
          const results = document.querySelectorAll(
            '#sic_description__listbox li:not(.autocomplete__option--no-results)'
          )

          if (results && results.length >= 1) {
            return true
          }

          return false
        }

        if (is_a_result_selected) {
          form.submit()
        } else {
          const error_message = document.querySelector(
            '[data-make-or-do-form] #event-name-error strong'
          )

          if (form_error_el) {
            form_error_el.classList =
              'govuk-form-group--error great-bring-to-front'

            if (is_sic_description_empty) {
              error_message.innerHTML = 'You must enter a product or service'
            }

            if (is_sic_description_unrecognised) {
              if (is_sic_results_available()) {
                error_message.innerHTML = 'Choose an option from the list below'
              } else {
                error_message.innerHTML =
                  'We do not recognise your product or service'
              }
            }
          }
        }
      })
    }
  },
}

const init_args = document.querySelector('[data-great-init-js]').dataset
  .greatInitJs

const sic_sector_data = JSON.parse(
  document.getElementById('sic_sector_data').textContent
)

if (sic_sector_data) {
  GreatFrontend.MakeOrDoSearchEnhanced.init(sic_sector_data, init_args)
}
