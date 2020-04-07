/* eslint-disable */
const slugify = function(string) {
  return string.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'');
}

export {
  slugify,
}
