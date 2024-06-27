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
function autocompleteFocusOnESC(parentInputID, dropdownID){
  const parentInput = document.querySelector(parentInputID)
  const dropdown = document.querySelector(dropdownID)
  // setTimeout is used because the autocomplete library sets the focused element to null on press of ESC via
  // https://github.com/alphagov/accessible-autocomplete/blob/79370c8c66f7496fb503bb1840cd590157f97232/src/autocomplete.js#L175
  dropdown.addEventListener("keydown", (e)=>{
      if (e.key == 'Escape'){
          setTimeout(()=>{
              parentInput.focus()
              parentInput.classList.add('autocomplete__input--focused')
          },1)
          setTimeout(()=>{
            dropdown.classList.remove('autocomplete__menu--visible')
            dropdown.classList.add('autocomplete__menu--hidden')
        },1)
      }
  })
  // remove focus styling when user navigates away from the dropdown.
  // element.addEventListener("focusout", (e)=>{
  //   element.classList.remove('autocomplete__input--focused')
  // })
}
