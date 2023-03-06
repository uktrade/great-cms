function customIOOSectorSuggest (query, populateResults) {
    const sectors = [
      { "Aerospace": ["aircraft design","component manufacturing","engines","maintenance","manufacturing and assembly","aeroplane","jet","helicopter","wings","turbofan","propellor","UAV","unmanned aerial vehicles"] },
      { "Automotive": ["cars","motorcycle","van","component manufacturing","bodies and coachwork","electronic components","engines and transmission","tyres","design","maintenance","manufacturing and assembly","agricultural machinery","bicycles","caravans","cars","lorries","motorcycles","trailers","motorsport","retail (automotive)"] },
      { "Food & Drink": ["casual dining","dining","alcoholic drinks","bakery products","brewing","dairy products","food and drink manufacturing","free from","allergen free food","frozen and chilled foods","fruit and vegetables","meat products","non-alcoholic drinks","cordial","juice drinks","organic food","pet food","ready meals","secondary food processing","bread","baking"] },
    ];
    let filteredSectors = sectors.filter(function (result) {
      if (!query) return [];
      const resultContains = Object.keys(result)[0].toLowerCase().indexOf(query.toLowerCase()) !== -1;
      const tags = Object.values(result)[0];
      let endonymContains = false;
      for (let i = 0; i < tags.length; i++) {
        if (endonymContains == true) { break; }
        endonymContains = tags[i].toLowerCase().indexOf(query.toLowerCase()) !== -1
      }
      return resultContains || endonymContains;
    });
    let sectorParentNames = [];
    for (let i = 0; i < filteredSectors.length; i++) {
      sectorParentNames.push(Object.keys(filteredSectors[i])[0]);
    }
    populateResults(
      sectorParentNames
    )
}

function onSubmitSector() {
    const autoCompleteSectorFieldValue = document.getElementById('js-sector-select').value;
    document.getElementById('js-sector-select-select').value = autoCompleteSectorFieldValue;
    window.localStorage.setItem('sector', autoCompleteSectorFieldValue);
}

function getSectorIfPreviouslySelected(fieldId) {
    const previouslySelectedSector = window.localStorage.getItem(fieldId) ? window.localStorage.getItem(fieldId): '';
    setTimeout(function() {
        document.getElementById('js-sector-select-select').value = previouslySelectedSector;
    }, 200);
    return previouslySelectedSector;
}

function onSubmitIntent() {
    let checkedValues = [];
    for (let i = 0; i < checkboxElements.length; i++) {
      checkboxElements[i].checked && checkedValues.push(document.getElementById('intent-select_' + i).value)
    }
    window.localStorage.setItem('intent', JSON.stringify(checkedValues));
    window.localStorage.setItem('intentOther', document.getElementById('id_intent_other').value);
  }

function getIntentIfPreviouslySelected() {
    const previouslySelectedIntent = window.localStorage.getItem('intent') ? JSON.parse(window.localStorage.getItem('intent')): [];
    const previouslySelectedIntentOther = window.localStorage.getItem('intentOther');
    if (previouslySelectedIntentOther) {
        document.getElementById('id_intent_other').value = previouslySelectedIntentOther;
        otherCheckboxElement.click();
    }
    for (let i = 0; i < previouslySelectedIntent.length; i++) {
        for (let o = 0; o < checkboxElements.length; o++) {
            if (previouslySelectedIntent[i] == checkboxElements[o].value) {
                checkboxElements[o].checked = true;
            }
        }
    }
}

function onSubmitLocation() {
    const autoCompleteSectorFieldValue = document.getElementById('js-location-select').value;
    document.getElementById('js-location-select-select').value = autoCompleteSectorFieldValue;
    window.localStorage.setItem('location', autoCompleteSectorFieldValue);
    window.localStorage.setItem('locationNone', document.getElementById('id_location_none').checked);
}

function getLocationIfPreviouslySelected(fieldId) {
    const previouslySelectedSector = window.localStorage.getItem(fieldId) ? window.localStorage.getItem(fieldId): '';
    setTimeout(function() {
        document.getElementById('js-location-select-select').value = previouslySelectedSector;
    }, 200);
    return previouslySelectedSector;
}

function getLocationNoneIfPreviouslySelected() {
    document.getElementById('id_location_none').checked = window.localStorage.getItem('locationNone') == 'true' ? true: false;
}

function onSubmitHiring() {
  const selectedRadioElement = document.querySelector('input[name="hiring"]:checked');
  if (selectedRadioElement) {
    window.localStorage.setItem('hiring', selectedRadioElement.value);
  }
}

function getHiringIfPreviouslySelected() {
  const previouslySelectedHiring = window.localStorage.getItem('hiring') ? window.localStorage.getItem('hiring') : '';

  const radioElements = document.getElementsByName('hiring');
  for (let i = 0; i < radioElements.length; i++) {
    if (radioElements[i].value == previouslySelectedHiring) {
      radioElements[i].checked = true;
    }
  }
}

function onSubmitSpend() {
  const selectedRadioElement = document.querySelector('input[name="spend"]:checked');
  if (selectedRadioElement) {
    window.localStorage.setItem('spend', selectedRadioElement.value);
    window.localStorage.setItem('spendOther', document.getElementById('id_spend_other').value);
  }
}

function getSpendIfPreviouslySelected() {
  const previouslySelectedSpend = window.localStorage.getItem('spend') ? window.localStorage.getItem('spend') : '';
  const previouslySelectedSpendOther = window.localStorage.getItem('spendOther');
  if (previouslySelectedSpendOther) {
      document.getElementById('id_spend_other').value = previouslySelectedSpendOther;
      otherRadioElement.click();
  }
  const radioElements = document.getElementsByName('spend');
  for (let i = 0; i < radioElements.length; i++) {
    if (radioElements[i].value == previouslySelectedSpend) {
      radioElements[i].checked = true;
    }
  }
}

function handleSpendRadioClick(radio) {
  if (otherRadioElement.checked == false) {
    document.getElementById('id_spend_other').value = '';
  }
}
