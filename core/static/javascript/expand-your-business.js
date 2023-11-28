function parseJsonForAutoComplete(json) {
  let out = [];
  for (let i = 0; i < json.length; i++) {
    const o = {};
    o[json[i]['en']] = json[i]['tags'];
    out.push(o);
  }
  return out;
}

function eybSectorSuggest (query, populateResults) {
  const sectorJson = [
    {
      "en":"Financial and Professional Services",
      "tags":["accountancy services","asset management","banking","commercial banking","digital banking","investment banking","private banking","retail banking","business and consumer services","commercial real estate services","contact centres","hr services","market research","marketing services","shared service centres","capital markets","hedge funds","private equity","venture capital","financial technology","blockchain and digital currencies","insurance technology","legal technology","property technology","regulatory technology","wealth technology","foreign exchange","insurance","commercial insurance","life insurance","motor insurance","travel insurance","legal services","commercial legal services","listings","management consultancy", "Sustainability", "Construction", "Intellectual Property", "Arbitration", "Environmental", "Net Zero", "Data Processing", "Construction Law", "Property Development", "Criminal Law", "Design", "Data", "Risk Advisory", "Audit", "Internet", "Data Management", "Professional Services", "Contracting", "Budgeting", "Rural Law", "Urban Law", "Savings", "Cross Border", "Deals", "Data Storing", "Real Estate", "Family Law", "Telecommunications", "Marketing", "Advertising", "Broadband", "It", "Services", "Event Management", "Human Capital", "Design Services", "Fashion Consultant", "Digital Share Broker", "Logistics", "Business Consultant", "Advertising", "Management Consultant", "Design", "Construction", "Design Consultant", "Divestment", "Software", "Development", "Computer", "Distribution", "Drop Shipping", "Human Resources", "Funding", "Cryptocurrency", "Fintech", "Advertising", "Solicitor", "Tax", "Advisory", "Investment", "Global Mobility", "Bitcoin", "Information", "Defence", "Consulting", "Advertising", "Business Services", "Insurtech", "Barrister", "Human Resources", "Mergers", "Takeovers", "Regulations", "Audit", "Shares", "Blockchain", "Hr Services", "Consultant", "Call Centre", "Legal", "Advisory", "Payroll", "Call Centre", "Immigration", "Payment Services", "Information Technology", "Insurance Services", "Customer Support", "Portfolio", "Lawtech", "Accounting", "Stocks", "Acquisitions", "Advertising", "Leasing", "Book Keeping", "Broking", "Risk Management", "Law", "Litigation", "Digital Consultant", "Audio", "News", "Ecommerce", "Venture Capital", "Underwriting", "Security", "Asset Management", "Disputes", "Infrastructure", "Financial Advisory", "Coffee", "Banking", "Investment", "Records", "Publishing", "Utilities", "Restaurants", "Boutique", "Tax", "Construction", "Dispute", "Building", "Tea", "Media", "Professional Services", "Travel", "Financial Services", "Wealth Management", "Tax Advisory", "Public Relations", "Recruitment", "Cloud Computing", "Recruitment Agencies", "Media", "Communications", "Cloud"]
    },
    {
      "en":"Food and Drink",
      "tags":["Hotels","Travel","Hospitality","casual dining","dining","alcoholic drinks","bakery products","brewing","dairy products","food and drink manufacturing","free from","allergen free food","frozen and chilled foods","fruit and vegetables","meat products","non-alcoholic drinks","cordial","juice drinks","organic food","pet food","ready meals","secondary food processing","bread","baking","food and beverage","food & beverage","beverage", "Agriculture", "Manufacturing", "Tech", "Production", "Food Processing Sector", "Commercial", "Fruit", "Private Chef", "Food Tech", "Eggs", "Food Disposal", "Sugar", "Water", "Hospitality", "Packaging Sectors", "Refreshments", "Wholesale", "Fine Dining", "Distillery", "Raw Material", "Food Refinement", "Ready Meals", "Storage Units", "Food Packaging", "Health Food", "Condiments", "Frozen Food", "Logistics", "Sustainable", "Livestock", "Beverages", "Food Transport", "Recipes", "Nutrition", "Free From", "Dairy Alternatives", "Transporting", "Allergens", "Events", "Peas", "Agriculture", "Soy", "Cocktails", "Supply Chain", "Catering", "Gin", "Farming", "Fishing", "Soft Drinks", "Fertilisers", "Plant Based", "Packaging", "Vegetables", "Celiac", "Gluten Free", "Sustainable Materials", "Hotels", "Distribution", "Nutritional Health", "Pubs, Bars", "Restaurant", "Lactose Free", "Brewery", "Dietitian", "Berries", "Seafood", "Delivery Technology", "Tea", "Chef", "Alternative", "Bars", "Organic", "Delivery", "Compost", "Hospitality", "Foodtech", "Health Foods", "Wine", "Processed Food", "Circular Economy", "Meat", "Gastro", "Fast Food Delivery", "Oil", "Retail Units", "Coffee"]
    },
    {
      "en":"Technology and Smart Cities",
      "tags":["Technology","Travel","ITSI Firm","Service implementation business","Information technologies","Management consulting business","Information technology","IT consulting","software","tech communications","telephone","telephony","VOIP","mobile phone","tech hardware","computer","Smart Phones", "Devices", "Electronics", "Lending", "Internet", "Safety", "Road", "Big Data", "Product Management", "Build", "Wifi", "Crypto", "Augmented", "Digital", "Aerospace", "Digital Advertising", "5G", "Digital Healthcare", "Property Development", "Tech Change", "Digital Assets", "Data Protection", "Machine Learning", "Biotech", "Smart Home", "Construction", "Application Design", "Video Advertising", "Tech Consulting", "Semi Conductor", "Renewable Energy", "Devops", "Architecture", "Web3", "Entertainment", "Renewables", "Fintech", "Internet", "Workplace Technology", "Research", "Online Banking", "Hotels", "Property Tech", "Solutions", "Gaming", "Smart Lighting", "Transport", "Blockchain", "Storage", "Service Design", "Transportation", "Software Development", "Net Zero", "Software", "Construction", "Internet", "Environmental Technologies", "Media", "Pharma Technology", "Cloud Based", "Internet Of Things", "Solution", "Delivery Manager", "Integration", "Digital Payments", "Agritech", "3G", "Smart Infrastructure", "Program", "Robotics", "Research", "Advertising", "Neo Banking", "Mortgage", "Engineer", "Accommodation", "Fibre Optics", "Digital Capital Raising", "It", "Ict", "Information Technology", "Design", "Green Tech", "Transportation", "Edtech", "Gas", "Electricity", "Water", "Cyber Security", "Intellectual Property", "Security", "Zero Carbon", "Software", "Mobile Banking", "App", "4G", "Ai", "Traffic", "Insurance", "Payments", "Lighting", "5G", "User", "Camera", "Digital", "Robotics", "Automation", "Mobile Phones", "Biotech", "Broadband", "Electric Vehicles", "Remote Learning", "Ecommerce", "Digital Investments", "Road", "Education", "Media", "Bills", "Design", "Carbon Free", "Education Tech", "Foodtech", "Data Management", "Sustainability", "Loans"]
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
      "en":"Defence and Security",
      "tags":["cyber security","cyber professional services","endpoint security","identification, authentication and access control","internet of things (iot) security","network security","supervisory control and data acquisition (scada) and industrial control systems (ics)","threat intelligence, monitoring, detection and analysis","physical security","border security","first responders","infrastructure","major events security","air","land","maritime","air electronic warfare","aircrew training","battlespace management","complex weapons","fast jet","ground based air defence","gbad","intelligence surveillance target acquisition and reconnaissance (istar)","large aircraft","platform protection","support and maintenance","unmanned air systems (uas)","chemical, biological, radiological and nuclear","(cbrn)","combat","combat support","counter explosive ordnance (c-eo)","cyber","maritime aviation","non-traditional and development","sub-surface","support and infrastructure","surface"]
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
      "en":"Oil and Gas",
      "tags":["petroleum","diesel","distilate","exploration","geology"]
    },
    {
      "en":"Rail",
      "tags":["train","freight","wagon","steam","locomotive","tram","carriage","station","railways","construction, fabrication and installation","operations and maintenance","planning, design and project delivery","strategic rail consultancy and advice","systems, rolling stock, equipment, plant and parts"]
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
