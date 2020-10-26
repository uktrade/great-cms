/* eslint-disable */

const slugify = function(string) {
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

const analytics = function(data) {
  const dataLayer = (window.dataLayer = window.dataLayer || [])
  dataLayer.push(data)
}

export {
  slugify,
  addItemToList,
  capitalize,
  analytics
}
