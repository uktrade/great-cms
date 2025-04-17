GreatFrontend = window.GreatFrontend || {}

GreatFrontend.SectorLookup = {
    init: (sectorData=[], selectElementToEnhanceID='js-sector-select', hasError=false) => {
        this.sectorData = sectorData
        accessibleAutocomplete.enhanceSelectElement({
            selectElement: document.getElementById(selectElementToEnhanceID),
            source: (query, populateResults) => {
                if (!query) return [];
                let results = [];
                for (let i = 0; i < this.sectorData.length; i++) {
                    const parentSector = this.sectorData[i].sector_name;
                    let subSector = this.sectorData[i].sub_sector_name || '';
                    let subSubSector = this.sectorData[i].sub_sub_sector_name || '';
                    if (parentSector.toLowerCase().indexOf(query.toLowerCase()) !== -1 || subSector.toLowerCase().indexOf(query.toLowerCase()) !== -1 || subSubSector.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
                        results.push(this.sectorData[i]);
                    }
                }

                results = results.sort((a, b) => {
                    if (a.sub_sub_sector_name && !b.sub_sub_sector_name) return -1;
                    if (!a.sub_sub_sector_name && b.sub_sub_sector_name) return 1;
        
                    // Sort alphabetically by sub_sub_sector_name if both are present
                    if (a.sub_sub_sector_name < b.sub_sub_sector_name) return -1;
                    if (a.sub_sub_sector_name > b.sub_sub_sector_name) return 1;
        
                    // Sort by presence of sub_sector_name if sub_sub_sector_name is equal
                    if (a.sub_sector_name && !b.sub_sector_name) return -1;
                    if (!a.sub_sector_name && b.sub_sector_name) return 1;
        
                    // Sort alphabetically by sub_sector_name if both are present or both are empty
                    if (a.sub_sector_name < b.sub_sector_name) return -1;
                    if (a.sub_sector_name > b.sub_sector_name) return 1;
        
                    // Sort alphabetically by sector_name if both sub_sub_sector_name and sub_sector_name are equal
                    if (a.sector_name < b.sector_name) return -1;
                    if (a.sector_name > b.sector_name) return 1;
        
                    return 0;
                })

                populateResults(results);
            },
            autoselect: false,
            defaultValue: '',
            templates: {
                inputValue: (selectedSectorRow) => {
                    if (selectedSectorRow) {
                        if (selectedSectorRow.sub_sub_sector_name) {
                            return selectedSectorRow.sub_sub_sector_name;
                        } else if (selectedSectorRow.sub_sector_name) {
                            return selectedSectorRow.sub_sector_name;
                        } else {
                            return selectedSectorRow.sector_name
                        }
                    } else {
                        return
                    }
                },
                suggestion: (selectedSectorRow) => {
                    if (typeof selectedSectorRow !== 'object') {
                        return selectedSectorRow
                    }
                    if (selectedSectorRow.sub_sub_sector_name) {
                        return `<span>${selectedSectorRow.sub_sub_sector_name}</span><br><span class='govuk-!-font-size-16 bgs-sector-lookup-second-row'>${selectedSectorRow.sector_name} &#8250; ${selectedSectorRow.sub_sector_name}</span>`;
                    } else if (selectedSectorRow.sub_sector_name) {
                        return `<span>${selectedSectorRow.sub_sector_name}</span><br><span class='govuk-!-font-size-16 bgs-sector-lookup-second-row'>${selectedSectorRow.sector_name}</span>`;
                    } else {
                        return `<span>${selectedSectorRow.sector_name}</span>`
                    }
                }
            },
            minLength: 2,
            onConfirm: function(selectedRow) {
                // onConfirm seems to be triggered by autocomplete many times passing null
                if (selectedRow) {
                    // When overriding onconfirm as per docs, it seems to then not automatically update
                    // the actual select elements selected value and so isnt posted on form submit
                    const sectorSelectInput = document.querySelector('#js-sector-select-select');
                    const setSectorSelectValue = (value) => {
                        for (let i = 0; i < sectorSelectInput.options.length; i++) {
                            if (sectorSelectInput.options[i].value === selectedRow.sector_id) {
                                sectorSelectInput.selectedIndex = i;
                                break;
                            }
                        }
                    }
                    setSectorSelectValue(selectedRow);
                }
            }
        });

        if (hasError) {
            const focusInput = setInterval(() => {
                const input = document.querySelector('#js-sector-select.autocomplete__input');
                if (input) {
                    clearInterval(focusInput);
                    input.focus();
                }
            }, 100);
        }
    },  
}
 
  // the autocomplete library we use has a known accessability issue when ESC is pressed
  // (see https://github.com/alphagov/accessible-autocomplete/issues/692)
  
  function showDropdown(dropdownElement, show) {
    if (show == true) {
      dropdownElement.classList.remove('autocomplete__menu--hidden')
      dropdownElement.classList.add('autocomplete__menu--visibile')
    } else {
      dropdownElement.classList.remove('autocomplete__menu--visible')
      dropdownElement.classList.add('autocomplete__menu--hidden')
    }
  }
  
  function focusInput(textInputElement) {
    textInputElement.focus()
    textInputElement.classList.add('autocomplete__input--focused')
  }
  
  function setCaretPositionToEnd(textInputElement) {
    const lenText = textInputElement.value.length
    textInputElement.setSelectionRange(lenText, lenText)
  }
  
  
  function autocompleteFocusOnESC(parentInputID, dropdownID) {
    const parentInput = document.querySelector(parentInputID)
    const dropdown = document.querySelector(dropdownID)
    // setTimeout is used because the autocomplete library sets the focused element to null on press of ESC via
    // https://github.com/alphagov/accessible-autocomplete/blob/79370c8c66f7496fb503bb1840cd590157f97232/src/autocomplete.js#L175 # /PS-IGNORE
    dropdown.addEventListener('keydown', (e) => {
      if (e.key == 'Escape') {
        setTimeout(() => {
          focusInput(parentInput)
        }, 1)
        setTimeout(() => {
          showDropdown(dropdown, false)
          setCaretPositionToEnd(parentInput)
        }, 1)
      }
    })
    parentInput.addEventListener('keydown', (e) => {
      // user presses esc on text input element (mouse navigation to select dropdown elements)
      if (e.key == 'Escape') {
        setTimeout(() => {
          focusInput(parentInput)
        }, 1)
      } else if (e.key != 'Tab') {
        // user has started typing again so show dropdown if num chars > 2 (value used when initilising auto complete library)
        setTimeout(() => {
          show = parentInput.value.length > 1
          showDropdown(dropdown, show)
        }, 1)
      }
    })
  }
