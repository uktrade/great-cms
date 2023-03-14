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

<<<<<<< HEAD
function parseJsonForAutoComplete(json) {
  let out = [];
  for (let i = 0; i < json.length; i++) {
    const o = {};
    o[json[i]['en']] = json[i]['tags'];
    out.push(o);
  }
  return out;
}

function customIOOSectorSuggest (query, populateResults) {
  const sectorJson = [
    {
      "en":"Financial and Professional Services",
      "tags":["accountancy services","asset management","banking","commercial banking","digital banking","investment banking","private banking","retail banking","business and consumer services","commercial real estate services","contact centres","hr services","market research","marketing services","shared service centres","capital markets","hedge funds","private equity","venture capital","financial technology","blockchain and digital currencies","insurance technology","legal technology","property technology","regulatory technology","wealth technology","foreign exchange","insurance","commercial insurance","life insurance","motor insurance","travel insurance","legal services","commercial legal services","listings","management consultancy"]
    },
    {
      "en":"Food and Drink",
      "tags":["casual dining","dining","alcoholic drinks","bakery products","brewing","dairy products","food and drink manufacturing","free from","allergen free food","frozen and chilled foods","fruit and vegetables","meat products","non-alcoholic drinks","cordial","juice drinks","organic food","pet food","ready meals","secondary food processing","bread","baking"]
    },
    {
      "en":"Technology and Smart Cities",
      "tags":["software","tech communications","telephone","telephony","VOIP","mobile phone","tech hardware","computer"]
    },
    {
      "en": "Advanced engineering",
      "tags":["mechanical, electrical and process engineering","metallurgical process plant","metals, minerals and materials","ceramics","composite materials","elastomers and rubbers","metals","Minerals","Plastics"]
    },
    {
      "en":"Aerospace",
      "tags":["aircraft design","component manufacturing","engines","maintenance","manufacturing and assembly","aeroplane","jet","helicopter","wings","turbofan","propellor","UAV","unmanned aerial vehicles"]
    },
    {
      "en":"Agriculture, Horticulture, Fisheries and pets",
      "tags":["arable crops","fertilisers and pesticides","seeds and plant varieties","soil management systems","engineering and precision farming","machinery","aquaculture","forestry","logging","fruit production","vegetable production","farming","livestock","horses","breeding stock","veterinary services","livestock feed","animal feed"]
    },
    {
      "en":"Airports",
      "tags":["Airports","infrastructure"]
    },
    {
      "en":"Automotive",
      "tags":["cars","motorcycle","van","component manufacturing","bodies and coachwork","electronic components","engines and transmission","tyres","design","maintenance","manufacturing and assembly","agricultural machinery","bicycles","caravans","cars","lorries","motorcycles","trailers","motorsport","retail (automotive)"]
    },
    {
      "en":"Biotech and Pharmaceuticals",
      "tags":["medical supplies","hospital","health","digital and data","manufacturing","pharmaceutical manufacturing","marketing and sales","professional services","research and development"]
    },
    {
      "en": "Business and consumer services",
      "tags":[""]
    },
    {
      "en": "Chemicals",
      "tags":["agricultural chemicals","basic chemicals","cleaning preparations","paint","adhesive products","synthetic materials"]
    },
    {
      "en": "Construction",
      "tags":["infrastructure"]
    },
    {
      "en":"Consumer and retail",
      "tags":["clothing","footwear","fashion","clothes","accessories","bags","luggage","apparel","leisure wear","sports wear","cosmetics","beauty","furniture","furnishings","consumer electronics","giftware","gifts","household goods","jewellry","leisure","tourism","shoes","jeans","travel","hotel","hospitality","supermarkets","tableware","textiles","interior textiles","carpets","books","printed media","stationery","musical instruments"]
    },
    {
      "en":"Creative industries",
      "tags":["design","digital services","equipment","experience economy","film and tv","games","immersive technology","music","performing arts","publishing","industrial design","interior design","agencies","social media platforms","photo and cinema","attractions","hardware","production and finance","sales and distribution","visual effects (vfx) and motion graphics","development","esports"]
    },
    {
      "en":"Defense and Security",
      "tags":["air","land","maritime","air electronic warfare","aircrew training","battlespace management","complex weapons","fast jet","ground based air defence","gbad","intelligence surveillance target acquisition and reconnaissance (istar)","large aircraft","platform protection","support and maintenance","unmanned air systems (uas)","chemical, biological, radiological and nuclear","(cbrn)","combat","combat support","counter explosive ordnance (c-eo)","cyber","maritime aviation","non-traditional and development","sub-surface","support and infrastructure","surface"]
    },
    {
      "en":"Education and Training",
      "tags":["curriculum, qualifications, assessment, inspection and quality assurance","early years","educational technology","english language training","higher education","schools","special educational needs and disabilities","support services","technical and vocational education and training","universities","consultancy and professional services","equipment and supplies","colleges and further education","teaching","school","university","teacher"]
    },
    {
      "en":"Energy",
      "tags":["civil nuclear","oil and gas","renewable energy","advanced technologies and small modular reactors","decommissioning","waste management","carbon capture technology and storage","biomass","electrical networks","energy storage","fixed-bottom offshore wind","floating offshore wind","off-shore","geothermal","hydro","hydrogen","industrial decarbonisation","low carbon heating","marine and tidal","onshore wind","on-shore","solar","waste to value","wave","tidal"]
    },
    {
      "en":"Environment",
      "tags":["environment","air pollution and noise control","clean growth services","environmental monitoring","marine pollution control","sanitation and remediation","waste management and recycling"]
    },
    {
      "en":"Healthcare and Medical",
      "tags":["digital and data","education and training","health systems management","infrastructure","lab services","laboratory services","pathology","social care"]
    },
    {
      "en":"Infrastructure Air and Sea",
      "tags":[""]
    },
    {
      "en":"Leisure",
      "tags":[""]
    },
    {
      "en":"Logistics",
      "tags":[""]
    },
    {
      "en":"Manufacturing",
      "tags":[""]
    },
    {
      "en":"Marine",
      "tags":[""]
    },
    {
      "en":"Maritime Services",
      "tags":["marine engineering","ports and terminals","infrastructure"]
    },
    {
      "en":"Medical devices and equipment",
      "tags":["diagnostics","medical diagnostics","digital and data","medical supplies and equipment"]
    },
    {
      "en":"Mining",
      "tags":["environmental monitoring and mine safety","exploration, research, finance and innovation","mine infrastructure and energy supply","mine operations and processing","mine waste management","mining vehicles, transport and equipment"]
    },
    {
      "en":"Nuclear",
      "tags":[""]
    },
    {
      "en":"Oil and Gas",
      "tags":["petroleum","diesel","distilate","exploration","geology"]
    },
    {
      "en":"Rail",
      "tags":["train","freight","wagon","steam","locomotive","tram","carriage","station","railways","construction, fabrication and installation","operations and maintenance","planning, design and project delivery","strategic rail consultancy and advice","systems, rolling stock, equipment, plant and parts"]
    },
    {
      "en":"Renewable",
      "tags":[""]
    },
    {
      "en":"Retail",
      "tags":[""]
    },
    {
      "en":"Security",
      "tags":["cyber security","cyber professional services","endpoint security","identification, authentication and access control","internet of things (iot) security","network security","supervisory control and data acquisition (scada) and industrial control systems (ics)","threat intelligence, monitoring, detection and analysis","physical security","border security","first responders","infrastructure","major events security"]
    },
    {
      "en":"Space",
      "tags":["rocket","propellant","satellite","orbital platforms","ground station","engineering"]
    },
    {
      "en":"Sports Events",
      "tags":["football","rugby","tennis","cycling","basketball","netball","table tennis","gymnastics","major sports events","sports infrastructure"]
    }
  ];
  const sectors = parseJsonForAutoComplete(sectorJson);
  populateResults(
    filterResults(sectors, query)
  )
}

function filterResults(data, query) {
  let filteredData = data.filter(function (result) {
=======
function customIOOSectorSuggest (query, populateResults) {
  const sectors = [
    { "Aerospace": ["aircraft design","component manufacturing","engines","maintenance","manufacturing and assembly","aeroplane","jet","helicopter","wings","turbofan","propellor","UAV","unmanned aerial vehicles"] },
    { "Automotive": ["cars","motorcycle","van","component manufacturing","bodies and coachwork","electronic components","engines and transmission","tyres","design","maintenance","manufacturing and assembly","agricultural machinery","bicycles","caravans","cars","lorries","motorcycles","trailers","motorsport","retail (automotive)"] },
    { "Food & Drink": ["casual dining","dining","alcoholic drinks","bakery products","brewing","dairy products","food and drink manufacturing","free from","allergen free food","frozen and chilled foods","fruit and vegetables","meat products","non-alcoholic drinks","cordial","juice drinks","organic food","pet food","ready meals","secondary food processing","bread","baking"] },
  ];
  let filteredSectors = sectors.filter(function (result) {
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))
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
<<<<<<< HEAD
  let dataParentNames = [];
  for (let i = 0; i < filteredData.length; i++) {
    dataParentNames.push(Object.keys(filteredData[i])[0]);
  }
  return dataParentNames;
}

function customIOOLocationSuggest (query, populateResults) {
  const locationJson = [
    {
      "en":"Wales",
      "tags":["Aberyswyth","Aberaeron","Ceredigion","Cardiff","Swansea","Bangor","Newport (Wales)","Gwent","Glamorgan","Carmarthen","Powys","Newquay (Wales)"]
    },
    {
      "en":"South West",
      "tags":["Devon","Cornwall","Saint Austell","Somerset","Dorset","Wiltshire","Newquay","Plymouth","Exmoor","Poole","Southampton","Exmouth","Bristol","Gloucestershire","Newquay (South West)"]
    },
    {
      "en":"Scotland",
      "tags":["Glasgow","Edinburgh","Highlands","Aberdeen","Inverness"]
    },
    {
      "en":"West Midlands",
      "tags":["Staffs","Staffordshire","Herefordshire","Worcs","Warwickshire","Birmingham","Solihull","Coventry","Dudley","Sandwell","Walsall","Wolverhampton"]
    },
    {
      "en":"London",
      "tags":["Westminster","Islington","Brixton","Lambeth","Chelsea","City","Clerkenwell","Covent Garden","Docklands","Hackney","Greater London"]
    },
    {
      "en":"East Midlands",
      "tags":[]
    },
    {
      "en":"North East",
      "tags":[]
    },
    {
      "en":"North West",
      "tags":[]
    },
    {
      "en":"Yorkshire and the Humber",
      "tags":[]
    },
    {
      "en":"East",
      "tags":[]
    },
    {
      "en":"South East",
      "tags":[]
    },
    {
      "en":"Northern Ireland",
      "tags":[]
    }
  ];
  const locations = parseJsonForAutoComplete(locationJson);
  populateResults(
    filterResults(locations, query)
=======
  let sectorParentNames = [];
  for (let i = 0; i < filteredSectors.length; i++) {
    sectorParentNames.push(Object.keys(filteredSectors[i])[0]);
  }
  populateResults(
    sectorParentNames
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))
  )
}

function onSubmitSector() {
<<<<<<< HEAD
  if (!document.getElementById('js-sector-select').value)
    document.getElementById('js-sector-select-select').value = '';
}

function onSubmitLocation() {
  if (!document.getElementById('js-location-select').value)
    document.getElementById('js-location-select-select').value = '';
=======
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
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))
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
