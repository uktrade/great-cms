/* eslint-disable */

const slugify = function(string) {
  return string.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'');
}

const addItemToList = (arr=[], i= 0, x= {}) => {
  let newArray = [...arr]
  arr[i] ? newArray[i] = {...newArray[i], ...x} : newArray = [...newArray, {...x}]
  return newArray
}


export {
  slugify,
  addItemToList
}


