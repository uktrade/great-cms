function onSubmitSector() {
  if (!document.getElementById('js-sector-select').value)
    document.getElementById('js-sector-select-select').value = '';
}

function onSubmitLocation() {
  if (!document.getElementById('js-location-select').value)
    document.getElementById('js-location-select-select').value = '';
}

function onSubmitProfile() {
  if (!document.getElementById('js-company-location-select').value)
    document.getElementById('js-company-location-select-select').value = '';
}

function handleSpendRadioClick(radio) {
  if (otherRadioElement.checked == false) {
    document.getElementById('id_spend_other').value = '';
  }
}

// the autocomplete library we use has a known accessability issue when ESC is pressed
// (see https://github.com/alphagov/accessible-autocomplete/issues/692)

function showDropdown(dropdownElement, show){
  if (show == true) {
    dropdownElement.classList.remove('autocomplete__menu--hidden')
    dropdownElement.classList.add('autocomplete__menu--visibile')
  } else {
    dropdownElement.classList.remove('autocomplete__menu--visible')
    dropdownElement.classList.add('autocomplete__menu--hidden')
  }
}

function focusInput(textInputElement){
  textInputElement.focus()
  textInputElement.classList.add('autocomplete__input--focused')
}

function setCaretPositionToEnd(textInputElement){
  const lenText = textInputElement.size
  textInputElement.setSelectionRange(lenText, lenText)
}


function autocompleteFocusOnESC(parentInputID, dropdownID){
  const parentInput = document.querySelector(parentInputID)
  const dropdown = document.querySelector(dropdownID)
  // setTimeout is used because the autocomplete library sets the focused element to null on press of ESC via
  // https://github.com/alphagov/accessible-autocomplete/blob/79370c8c66f7496fb503bb1840cd590157f97232/src/autocomplete.js#L175
  dropdown.addEventListener("keydown", (e)=>{
      if (e.key == 'Escape'){
          setTimeout(()=>{
            focusInput(parentInput)
          }, 1)
          setTimeout(()=>{
            showDropdown(dropdown, false)
            setCaretPositionToEnd(parentInput)
          }, 1)
      }
  })
  parentInput.addEventListener("keydown", (e)=>{
    // user presses esc on text input element (mouse navigation to select dropdown elements)
    if (e.key == 'Escape'){
      setTimeout(()=>{
        focusInput(parentInput)
      }, 1)
    } else if (e.key != 'Tab') {
      // user has started typing again so show dropdown
      setTimeout(()=>{
        showDropdown(dropdown, true)
      }, 1)
    }
  })
}
