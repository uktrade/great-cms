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
      "tags":["casual dining","dining","alcoholic drinks","bakery products","brewing","dairy products","food and drink manufacturing","free from","allergen free food","frozen and chilled foods","fruit and vegetables","meat products","non-alcoholic drinks","cordial","juice drinks","organic food","pet food","ready meals","secondary food processing","bread","baking","food and beverage","food & beverage","beverage"]
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
      "tags":["Isle of Anglesey","Gwynedd","Conwy","Denbighshire","Flintshire","Wrexham","Ceredigion","Pembrokeshire","Carmarthenshire","Swansea","Neath Port Talbot","Bridgend","Vale of Glamorgan","Cardiff","Rhondda Cynon Taf","Caerphilly","Blaenau Gwent","Torfaen","Monmouthshire","Newport","Powys","Merthyr Tydfil"]
    },
    {
      "en":"South West",
      "tags":["Bath and North East Somerset","Bristol","North Somerset","South Gloucestershire","Plymouth","Torbay","Swindon","Cornwall","Isles of Scilly","Wiltshire","Bournemouth, Christchurch and Poole","Dorset","East Devon","Exeter","Mid Devon","North Devon","South Hams","Teignbridge","Torridge","West Devon","Cheltenham","Cotswold","Forest of Dean","Gloucester","Stroud","Tewkesbury","Mendip","Sedgemoor","South Somerset","Somerset West and Taunton"]
    },
    {
      "en":"Scotland",
      "tags":["Glasgow","Edinburgh","Aberdeen","Dundee","Paisley","East Kilbride","Livingston","Dunfermline","Hamilton","Inverness","Cumbernauld","Kirkcaldy","Perth","Kilmarnock","Dumfries","Ayr","Coatbridge","Greenock","Glenrothes","Stirling","Airdrie","Falkirk","Irvine","Motherwell","Rutherglen","Cambuslang","Wishaw","Bearsden","Newton Mearns","Clydebank","Elgin","Renfrew","Bishopbriggs","Bathgate","Arbroath","Kirkintilloch","Musselburgh","Dumbarton","Bellshill","Peterhead","St Andrews","Bonnyrigg","Barrhead","Blantyre","Penicuik","Grangemouth","Kilwinning","Broxburn","Johnstone","Viewpark","Larkhall","Erskine"]
    },
    {
      "en":"West Midlands",
      "tags":["Herefordshire, County of","Telford and Wrekin","Stoke-on-Trent","Shropshire","Cannock Chase","East Staffordshire","Lichfield","Newcastle-under-Lyme","South Staffordshire","Stafford","Staffordshire Moorlands","Tamworth","North Warwickshire","Nuneaton and Bedworth","Rugby","Stratford-on-Avon","Warwick","Bromsgrove","Malvern Hills","Redditch","Worcester","Wychavon","Wyre Forest","Birmingham","Coventry","Dudley","Sandwell","Solihull","Walsall","Wolverhampton"]
    },
    {
      "en":"London",
      "tags":["City of London","Barking and Dagenham","Barnet","Bexley","Brent","Bromley","Camden","Croydon","Ealing","Enfield","Greenwich","Hackney","Hammersmith and Fulham","Haringey","Harrow","Havering","Hillingdon","Hounslow","Islington","Kensington and Chelsea","Kingston upon Thames","Lambeth","Lewisham","Merton","Newham","Redbridge","Richmond upon Thames","Southwark","Sutton","Tower Hamlets","Waltham Forest","Wandsworth","Westminster","Park Royal","Canning Town","Acton","Greenford","Staples Corner","Heathrow","Hayes","Tottenham","Wembley","Woolwich","Uxbridge","Barking","Dagenham","London (City)","London (West End – Bond Street)","London (West End – Oxford Street)","London (West End)","London (East)","London - New Bond Street","Greater London","London"]
    },
    {
      "en":"East Midlands",
      "tags":["Derby","Leicester","Rutland","Nottingham","North Northamptonshire ","West Northamptonshire ","Amber Valley","Bolsover","Chesterfield","Derbyshire Dales","Erewash","High Peak","North East Derbyshire","South Derbyshire","Blaby","Charnwood","Harborough","Hinckley and Bosworth","Melton","North West Leicestershire","Oadby and Wigston","Boston","East Lindsey","Lincoln","North Kesteven","South Holland","South Kesteven","West Lindsey","Ashfield","Bassetlaw","Broxtowe","Gedling","Mansfield","Newark and Sherwood","Rushcliffe"]
    },
    {
      "en":"North East",
      "tags":["Hartlepool","Middlesbrough","Redcar and Cleveland","Stockton-on-Tees","Darlington","County Durham","Northumberland","Newcastle upon Tyne","North Tyneside","South Tyneside","Sunderland","Gateshead"]
    },
    {
      "en":"North West",
      "tags":["Halton","Warrington","Blackburn with Darwen","Blackpool","Cheshire East","Cheshire West and Chester","Allerdale","Barrow-in-Furness","Carlisle","Copeland","Eden","South Lakeland","Burnley","Chorley","Fylde","Hyndburn","Lancaster","Pendle","Preston","Ribble Valley","Rossendale","South Ribble","West Lancashire","Wyre","Bolton","Bury","Manchester","Oldham","Rochdale","Salford","Stockport","Tameside","Trafford","Wigan","Knowsley","Liverpool","St. Helens","Sefton","Wirral"]
    },
    {
      "en":"Yorkshire and the Humber",
      "tags":["Kingston upon Hull","East Riding of Yorkshire","North East Lincolnshire","North Lincolnshire","York","Craven","Hambleton","Harrogate","Richmondshire","Ryedale","Scarborough","Selby","Barnsley","Doncaster","Rotherham","Sheffield","Bradford","Calderdale","Kirklees","Leeds","Wakefield"]
    },
    {
      "en":"East",
      "tags":["Peterborough","Luton","Southend-on-Sea","Thurrock","Bedford","Central Bedfordshire","Cambridge","East Cambridgeshire","Fenland","Huntingdonshire","South Cambridgeshire","Basildon","Braintree","Brentwood","Castle Point","Chelmsford","Colchester","Epping Forest","Harlow","Maldon","Rochford","Tendring","Uttlesford","Broxbourne","Dacorum","Hertsmere","North Hertfordshire","Three Rivers","Watford","Breckland","Broadland","Great Yarmouth","King's Lynn and West Norfolk","North Norfolk","Norwich","South Norfolk","Babergh","Ipswich","Mid Suffolk","St Albans","Welwyn Hatfield","East Hertfordshire","Stevenage","East Suffolk","West Suffolk","Borehamwood","Welwyn Garden City","Hemel Hempstead","Dunstable","West Thurrock"]
    },
    {
      "en":"South East",
      "tags":["Medway","Bracknell Forest","West Berkshire","Reading","Slough","Windsor and Maidenhead","Wokingham","Milton Keynes","Brighton and Hove","Portsmouth","Southampton","Isle of Wight","Buckinghamshire","Eastbourne","Hastings","Lewes","Rother","Wealden","Basingstoke and Deane","East Hampshire","Eastleigh","Fareham","Gosport","Hart","Havant","New Forest","Rushmoor","Test Valley","Winchester","Ashford","Canterbury","Dartford","Dover","Gravesham","Maidstone","Sevenoaks","Folkestone and Hythe","Swale","Thanet","Tonbridge and Malling","Tunbridge Wells","Cherwell","Oxford","South Oxfordshire","Vale of White Horse","West Oxfordshire","Elmbridge","Epsom and Ewell","Guildford","Mole Valley","Reigate and Banstead","Runnymede","Spelthorne","Surrey Heath","Tandridge","Waverley","Woking","Adur","Arun","Chichester","Crawley","Horsham","Mid Sussex","Worthing","Sunbury","Weybridge","Brighton","Camberley","High Wycombe","Redhill","Bracknell","Basingstoke","Aylesbury","Newbury","Andover"]
    },
    {
      "en":"Northern Ireland",
      "tags":["Belfast","Derry","Craigavon","Newtownabbey","Bangor","Lisburn","Ballymena","Newtownards","Newry","Carrickfergus"]
    }
  ];
  const locations = parseJsonForAutoComplete(locationJson);
  populateResults(
    filterResults(locations, query)
  )
}

function onSubmitSector() {
  if (!document.getElementById('js-sector-select').value)
    document.getElementById('js-sector-select-select').value = '';
}

function onSubmitLocation() {
  if (!document.getElementById('js-location-select').value)
    document.getElementById('js-location-select-select').value = '';
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
