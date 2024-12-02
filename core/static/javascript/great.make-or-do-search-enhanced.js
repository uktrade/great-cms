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
              keyword_parts = keywords.split(', ')
            }

            if (search_input && keyword_parts) {
              let keyword_match = ''

              keyword_parts.forEach((keyword) => {
                if (keyword.includes(search_input.value)) {
                  keyword_match = keyword
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
            is_keyword_match = keywords.includes(make_or_do_keyword.value)

            let keyword_match = ''

            keyword_parts = keywords.split(', ')

            keyword_parts.forEach((keyword) => {
              if (keyword.includes(make_or_do_keyword.value)) {
                keyword_match = keyword
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
            }
          }, 10)
        }
      },
      placeholder: 'For example, financial services or coffee',
      inputClasses: 'govuk-input great-text-input great-ds-autocomplete-input',
      menuClasses: 'great-autocomplete-overlay',
      required: true,
      showNoOptionsFound: false,
    })

    const clear_search_button = document.querySelector('#clear_search')
    const sic_description = document.querySelector('#sic_description')

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
  },
}
