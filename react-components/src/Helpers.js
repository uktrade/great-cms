/* eslint-disable */

const slugify = (string) => {
  return string.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '');
}

const addItemToList = (arr = [], i = 0, x = {}) => {
  let newArray = [...arr]
  arr[i] ? newArray[i] = { ...newArray[i], ...x } : newArray = [...newArray, { ...x }]
  return newArray
}

const capitalize = (str, enable = true) => {
  // Capitalize the first lettter and replace underscores with spaces 
  const strWithSpaces = str.replace(/_/g, ' ')
  return enable ? strWithSpaces.charAt(0).toUpperCase() + strWithSpaces.slice(1) : strWithSpaces
}

const analytics = (data) => {
  const dataLayer = (window.dataLayer = window.dataLayer || [])
  dataLayer.push(data)
}

const sectionQuestionMapping =  {
 'story': 'How you started',
 'location': 'Where you\'re based',
 'processes': 'How you make your products',
 'packaging': 'Your product packaging',
 'performance' : 'Your business performance',
 'rationale': 'Why you want to export',
 'demand': 'Describe the consumer demand for your product in the selected country',
 'competitors': 'Who are your competitors in the selected country?',
 'trend': 'What are the product trends in the selected country?',
 'unqiue_selling_proposition': 'What’s your unique selling proposition for the selected country?',
 'average_price': 'What’s the avg price for your product in the selected country?'
}

export {
  slugify,
  addItemToList,
  capitalize,
  analytics,
  sectionQuestionMapping
}
