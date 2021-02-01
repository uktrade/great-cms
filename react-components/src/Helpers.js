const slugify = (string) => {
  return string
    .toLowerCase()
    .replace(/ /g, '-')
    .replace(/[^\w-]+/g, '')
}

const addItemToList = (arr = [], i = 0, x = {}) => {
  let newArray = [...arr]
  arr[i]
    ? (newArray[i] = { ...newArray[i], ...x })
    : (newArray = [...newArray, { ...x }])
  return newArray
}

const capitalize = (str, enable = true) => {
  // Capitalize the first lettter and replace underscores with spaces
  const strWithSpaces = str.replace(/_/g, ' ')
  return enable
    ? strWithSpaces.charAt(0).toUpperCase() + strWithSpaces.slice(1)
    : strWithSpaces
}

const analytics = (data) => {
  const dataLayer = (window.dataLayer = window.dataLayer || [])
  dataLayer.push(data)
}

const normaliseValues = (str, places = 1, fixed = false) => {
  const pow = Math.pow(10, places)
  if (str) {
    var values = String(str).replace(/\d+(\.\d+)?/g, ($0) => {
      return fixed
        ? parseFloat($0).toFixed(places)
        : Math.round(parseFloat($0) * pow) / pow
    })
    values = values.replace(/\d+(\.\d+)?(?=\%)/g, ($0) => {
      return Math.round($0)
    })
    return values.split(/\(([^)]+)\)/)
  } else {
    return 'Data not available'
  }
}

let millify = (value) => {
  const floatValue = parseFloat(value)
  if (floatValue) {
    const names = ['million', 'billion', 'trillion']
    const oom = Math.floor(Math.log10(Math.abs(floatValue)) / 3)
    if (oom <= 1) return Math.round(floatValue).toLocaleString()
    return `${(value / Math.pow(10, oom * 3)).toFixed(1)} ${names[oom - 2]}`
  }
  return value === null ? value : ''+value
}

const stripPercentage = (str) => {
  // The regular expression matches an integer or float with or without leading
  // digit at the end of the string, not necessarily preceded by a space and not
  // necessarily succeded  by a percent symbol.
  // e.g. 'text.1(+)(%)', 'text .1(+)(%)', 'text 1(+).1(+)(%)' and combinations
  if (str) {
    const regex = /\s?\<?\>?\.?\d*\.?\d+\%?$/
    return str.replace(regex, '')
  }

  return str
}

const isObject = (obj) => {
  return Object.prototype.toString.call(obj) === '[object Object]'
}

const isArray = (arr) => {
  return Object.prototype.toString.call(arr) === '[object Array]'
}

const get = (obj, path, def=null) => {
  // get a value from an object based on dot-separated path
  let out = obj
  const pathSplit = path.split('.')
  for (var i = 0; i < pathSplit.length; i++) {
    if (!isObject(out)) {
      return def
    }
    out = out[pathSplit[i]]
  }
  return out
}

const mapArray = (array, key) => {
  // Generates an object from an array, using the given key
  const out = {}
  array.forEach((entry) => {
    out[entry[key]] = entry
  })
  return out
}

const sectionQuestionMapping = {
  story: 'How you started',
  location: "Where you're based",
  processes: 'How you make your products',
  packaging: 'Your product packaging',
  performance: 'Your business performance',
  rationale: 'Why you want to export',
  demand:
    'Describe the consumer demand for your product in the selected country',
  competitors: 'Who are your competitors in the selected country?',
  trend: 'What are the product trends in the selected country?',
  unqiue_selling_proposition:
    'What’s your unique selling proposition for the selected country?',
  average_price:
    'What’s the avg price for your product in the selected country?',
}

const getLabel = (list, selected) => {
  const hasValue = list.find((x) => x.value === selected)
  return selected && hasValue ? hasValue.label : ''
}

const getValue = (list, selected) => {
  const hasLabel = list.find((x) => x.label === selected)
  return selected && hasLabel ? hasLabel.value : ''
}

const formatLessonLearned = (lesson, section, id) =>
  lesson[section.lessons[id]]
    ? {
        ...lesson[section.lessons[id]],
        url: `${lesson[section.lessons[id]].url}?return-link=${section.url}`,
      }
    : {}

export {
  slugify,
  addItemToList,
  capitalize,
  analytics,
  sectionQuestionMapping,
  normaliseValues,
  isObject,
  isArray,
  get,
  mapArray,
  getLabel,
  getValue,
  formatLessonLearned,
  millify,
  stripPercentage,
}
