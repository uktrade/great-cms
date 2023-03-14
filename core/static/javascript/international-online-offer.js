const iooFormData = {
  triageInfromation: {
    sector: '',
    intent: [],
    intentOther: '',
    location: '',
    locationOther: '',
    hiring: '',
    spend: '',
    spendOther: '',
  },
  contactInformation: {
    companyName: '',
    companyLocation: '',
    fullName: '',
    role: '',
    email: '',
    telephoneNumber: '',
    agreeTerms: false,
    agreeInfoEmail: false,
    agreeInfoTelephone: false,
  },
  contactFormComplete: false,
}

function getIooFormData() {
  if (window.localStorage.getItem('iooFormData')) {
    return JSON.parse(window.localStorage.getItem('iooFormData'));
  } else {
    return iooFormData;
  }
}

function setIooFormData(newData) {
  window.localStorage.setItem('iooFormData', JSON.stringify(newData));
}

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
  const iooFormData = getIooFormData();
  document.getElementById('js-sector-select-select').value = document.getElementById('js-sector-select').value;
  iooFormData.triageInfromation.sector = document.getElementById('js-sector-select').value;
  setIooFormData(iooFormData);
}

function getSectorIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  setTimeout(function() {
      document.getElementById('js-sector-select-select').value = iooFormData.triageInfromation.sector;
  }, 200);
  return iooFormData.triageInfromation.sector;
}

function onSubmitIntent() {
  const iooFormData = getIooFormData();
  let checkedValues = [];
  for (let i = 0; i < checkboxElements.length; i++) {
    checkboxElements[i].checked && checkedValues.push(document.getElementById('intent-select_' + i).value)
  }
  iooFormData.triageInfromation.intent = checkedValues;
  iooFormData.triageInfromation.intentOther = document.getElementById('id_intent_other').value;
  setIooFormData(iooFormData);
}

function getIntentIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  if (iooFormData.triageInfromation.intentOther) {
      document.getElementById('id_intent_other').value = iooFormData.triageInfromation.intentOther;
      otherCheckboxElement.click();
  }
  for (let i = 0; i < iooFormData.triageInfromation.intent.length; i++) {
      for (let o = 0; o < checkboxElements.length; o++) {
          if (iooFormData.triageInfromation.intent[i] == checkboxElements[o].value) {
              checkboxElements[o].checked = true;
          }
      }
  }
}

function onSubmitLocation() {
  const iooFormData = getIooFormData();
  document.getElementById('js-location-select-select').value = document.getElementById('js-location-select').value;
  iooFormData.triageInfromation.location = document.getElementById('js-location-select').value;
  iooFormData.triageInfromation.locationOther = document.getElementById('id_location_none').checked;
  setIooFormData(iooFormData);
}

function getLocationIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  setTimeout(function() {
    document.getElementById('js-location-select-select').value = iooFormData.triageInfromation.location;
  }, 200);
  return iooFormData.triageInfromation.location;
}

function getLocationNoneIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  document.getElementById('id_location_none').checked = iooFormData.triageInfromation.locationOther
}

function onSubmitHiring() {
  const iooFormData = getIooFormData();
  const selectedRadioElement = document.querySelector('input[name="hiring"]:checked');
  if (selectedRadioElement) {
    iooFormData.triageInfromation.hiring = selectedRadioElement.value;
    setIooFormData(iooFormData);
  }
}

function getHiringIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  const radioElements = document.getElementsByName('hiring');
  for (let i = 0; i < radioElements.length; i++) {
    if (radioElements[i].value == iooFormData.triageInfromation.hiring) {
      radioElements[i].checked = true;
    }
  }
}

function onSubmitSpend() {
  const iooFormData = getIooFormData();
  const selectedRadioElement = document.querySelector('input[name="spend"]:checked');
  if (selectedRadioElement) {
    iooFormData.triageInfromation.spend = selectedRadioElement.value;
    iooFormData.triageInfromation.spendOther = document.getElementById('id_spend_other').value;
    setIooFormData(iooFormData);
  }
}

function getSpendIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  document.getElementById('id_spend_other').value = iooFormData.triageInfromation.spendOther;
  if (iooFormData.triageInfromation.spendOther) {
      otherRadioElement.click();
  }
  const radioElements = document.getElementsByName('spend');
  for (let i = 0; i < radioElements.length; i++) {
    if (radioElements[i].value == iooFormData.triageInfromation.spend) {
      radioElements[i].checked = true;
    }
  }
}

function handleSpendRadioClick(radio) {
  if (otherRadioElement.checked == false) {
    document.getElementById('id_spend_other').value = '';
  }
}

function onSubmitContact() {
  const iooFormData = getIooFormData();
  iooFormData.contactFormComplete = false;
  const companyLocation = document.getElementById('js-company-location-select').value;
  window.localStorage.removeItem('completedContactForm');
  document.getElementById('js-company-location-select-select').value = companyLocation;
  iooFormData.contactInformation.companyName = document.getElementById('id_company_name').value;
  iooFormData.contactInformation.companyLocation = companyLocation;
  iooFormData.contactInformation.fullName = document.getElementById('id_full_name').value;
  iooFormData.contactInformation.role = document.getElementById('id_role').value;
  iooFormData.contactInformation.email = document.getElementById('id_email').value;
  iooFormData.contactInformation.telephoneNumber = document.getElementById('id_telephone_number').value;
  iooFormData.contactInformation.agreeTerms = document.getElementById('id_agree_terms').checked;
  iooFormData.contactInformation.agreeInfoEmail = document.getElementById('id_agree_info_email').checked;
  iooFormData.contactInformation.agreeInfoTelephone = document.getElementById('id_agree_info_telephone').checked;
  setIooFormData(iooFormData);
}

function getContactFormIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  document.getElementById('id_company_name').value = iooFormData.contactInformation.companyName;
  document.getElementById('id_full_name').value = iooFormData.contactInformation.fullName;
  document.getElementById('id_role').value = iooFormData.contactInformation.role;
  document.getElementById('id_email').value = iooFormData.contactInformation.email;
  document.getElementById('id_telephone_number').value = iooFormData.contactInformation.telephoneNumber;
  document.getElementById('id_agree_terms').checked = iooFormData.contactInformation.agreeTerms;
  document.getElementById('id_agree_info_email').checked = iooFormData.contactInformation.agreeInfoEmail;
  document.getElementById('id_agree_info_telephone').checked = iooFormData.contactInformation.agreeInfoTelephone;
  setTimeout(function() {
    document.getElementById('js-company-location-select-select').value = iooFormData.contactInformation.companyLocation;
  }, 200);
}

function getContactFormCompanyLocationIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  return iooFormData.contactInformation.companyLocation;
}

function hideMessagesToCompleteContactFormIfPreviouslySelected() {
  const iooFormData = getIooFormData();
  if (iooFormData.contactFormComplete) {
    if (document.getElementById('completed_contact_form_message')) document.getElementById('completed_contact_form_message').style.display = 'none';
    if (document.getElementById('complete_contact_form_message')) document.getElementById('complete_contact_form_message').style.display = 'none';
  }
}

function saveIfContactFormSuccess() {
  const iooFormData = getIooFormData();
  if (document.getElementById('completed_contact_form_message')) {
    iooFormData.contactFormComplete = true;
    setIooFormData(iooFormData);
  }
}
