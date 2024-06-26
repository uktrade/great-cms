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

// the autocomplete library we use has a known accessability issue (see https://github.com/alphagov/accessible-autocomplete/issues/692)
// whereby if users press esc on the autocomplete dropdown list focus is lost from the input element.
// below is a workaround to accomodate this.
function autocompleteFocusOnESC(elementName){
  const element = document.querySelector(elementName)
  // return focus to input if esc is pressed on autocomplete list
  element.addEventListener("keydown", (e)=>{
      if (e.key == 'Escape'){
          setTimeout(()=>{
              element.focus()
              element.classList.add('autocomplete__input--focused')
          },2)
      }
  })
  // remove focus styling when user navigates away from the dropdown.
  element.addEventListener("focusout", (e)=>{
    element.classList.remove('autocomplete__input--focused')
  })
}
