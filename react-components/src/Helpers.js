export const dateNowISO = () => new Date().toISOString().slice(0, 10)

export const dateFormat = (date = dateNowISO()) => {
  // Requires ISO formatted date: YYYY-MM-DD
  const [year, month, day] = date.split('-')
  const months = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec',
  }

  return `${day} ${months[month]} ${year}`
}

export const slugify = (string) => {
  return string
    .toLowerCase()
    .replace(/ /g, '-')
    .replace(/[^\w-]+/g, '')
}

export const addItemToList = (arr = [], i = 0, x = {}) => {
  let newArray = [...arr]
  arr[i]
    ? (newArray[i] = { ...newArray[i], ...x })
    : (newArray = [...newArray, { ...x }])
  return newArray
}

export const capitalize = (str, enable = true) => {
  // Capitalize the first lettter and replace underscores with spaces
  const strWithSpaces = str.replace(/_/g, ' ')
  return enable
    ? strWithSpaces.charAt(0).toUpperCase() + strWithSpaces.slice(1)
    : strWithSpaces
}

export const analytics = (data) => {
  const dataLayer = (window.dataLayer = window.dataLayer || [])
  dataLayer.push(data)
}

export const normaliseValues = (str, places = 1, fixed = false) => {
  const pow = 10 ** places
  if (str) {
    let values = String(str).replace(/\d+(\.\d+)?/g, ($0) => {
      return fixed
        ? parseFloat($0).toFixed(places)
        : Math.round(parseFloat($0) * pow) / pow
    })
    values = values.replace(/\d+(\.\d+)?(?=%)/g, ($0) => {
      return Math.round($0)
    })
    return values.split(/\(([^)]+)\)/)
  }
  return 'Data not available'
}

export const numberWithSign = (value) => {
  return Number.isFinite(value - 0)
    ? `${['-', '', '+'][Math.sign(value) + 1]}${Math.abs(value)}`
    : value
}

export const millify = (value) => {
  const floatValue = parseFloat(value)
  if (floatValue) {
    const names = ['million', 'billion', 'trillion']
    const oom = Math.floor(Math.log10(Math.abs(floatValue)) / 3)
    if (oom <= 1) return Math.round(floatValue).toLocaleString()
    return `${(value / 10 ** (oom * 3)).toFixed(1)} ${names[oom - 2]}`
  }
  return value === null ? value : `${value}`
}

export const stripPercentage = (str) => {
  // The regular expression matches an integer or float with or without leading
  // digit at the end of the string, not necessarily preceded by a space and not
  // necessarily succeded  by a percent symbol.
  // e.g. 'text.1(+)(%)', 'text .1(+)(%)', 'text 1(+).1(+)(%)' and combinations
  if (str) {
    const regex = /\s?<?>?\.?\d*\.?\d+%?$/
    return str.replace(regex, '')
  }

  return str
}

export const listJoin = (arr) => {
  // Joins an array of strings with commas and a closing 'and'
  return arr.reduce((acc, str, index) => {
    let sep = ''
    if (index) {
      sep = index === arr.length - 1 ? ' and ' : ', '
    }
    return `${acc}${sep}${str}`
  }, '')
}

export const isObject = (obj) => {
  return Object.prototype.toString.call(obj) === '[object Object]'
}

export const isArray = (arr) => {
  return Object.prototype.toString.call(arr) === '[object Array]'
}

export const isFunction = (fn) => {
  return !!(fn && fn.constructor && fn.call && fn.apply)
}

export const get = (obj, path, def = null) => {
  // get a value from an object based on dot-separated path
  let out = obj
  const pathSplit = path.split('.')
  for (let i = 0; i < pathSplit.length; i += 1) {
    if (isObject(out) || isArray(out)) {
      out = out[pathSplit[i]]
    } else {
      return def
    }
  }
  return out
}

export const mapArray = (array, key) => {
  // Generates an object from an array, using the given key
  const out = {}
  array.forEach((entry) => {
    out[entry[key]] = entry
  })
  return out
}

export const deepAssign = (obj1, obj2) => {
  const out = { ...obj1 }
  Object.keys(obj2).forEach((key) => {
    if (out[key] && isObject(out[key]) && isObject(obj2[key])) {
      out[key] = deepAssign(out[key], obj2[key])
    } else {
      out[key] = obj2[key]
    }
  })
  return out
}

export const deepEqual = (obj1, obj2) => {
  if (Object.keys(obj1).length !== Object.keys(obj2).length) return false
  for (const key in obj1) if (obj1.hasOwnProperty(key)) {
    if (isObject(obj1[key]) && isObject(obj2[key])) {
      if (!deepEqual(obj1[key], obj2[key])) return false
    } else if (obj1[key] !== obj2[key]) return false
  }
  return true
}

export const camelize = (str) => {
  return str
    .split('_')
    .reduce(
      (acc, part) =>
        acc ? `${acc}${part.charAt(0).toUpperCase()}${part.slice(1)}` : part,
      '',
    )
}

export const camelizeObject = (obj) => {
  return Object.keys(obj).reduce((out, key) => {
    out[camelize(key)] = obj[key]
    return out
  }, {})
}

export const sectionQuestionMapping = {
  story: 'How you started',
  location: 'Where you\'re based',
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

export const formatLessonLearned = (lesson, section, id) =>
  lesson[section.lessons[id]]
    ? {
      ...lesson[section.lessons[id]],
      url: `${lesson[section.lessons[id]].url}?return-link=${section.url}`,
    }
    : {}

export const objectHasValue = (object = {}) => Object.values(object).some((x) => x)

export const validation = {
  onlyOneZero: (t, value) =>
    value ? t === 0 && value.length === 1 && value.charAt(0) === '0' : false,
  twoDecimal: (number) => {
    const regx = /^[0-9]*(\.[0-9][0-9]?)?$/g
    return regx.test(number)
  },
  wholeNumber: (number) => {
    const regx = /^[\d]*$/g
    return regx.test(number)
  },
}

export const prependThe = (str) =>
  [
    'Central African Republic',
    'Comoros',
    'Czechia',
    'Dominican Republic',
    'Ivory Coast',
    'Maldives',
    'Marshall Islands',
    'Netherlands',
    'Philippines',
    'Solomon Islands',
    'United Arab Emirates',
    'United States',
  ].includes(str)
    ? `the ${str}`
    : str

export const sortBy = (arr, key) =>
// return array sorted by the given key case insensitive
  [...arr].sort((p1, p2) =>
    (p1[key] || '').toLowerCase() > (p2[key] || '').toLowerCase() ? 1 : -1
  )

export const sortMapBy = (arr, key) =>
// return a case insensitive sorting map from the current array based on the key provided
  [...Array((arr || []).length).keys()].sort((i1, i2) =>
    (arr[i1][key] || '').toLowerCase() >
    (arr[i2][key] || '').toLowerCase()
      ? 1
      : -1,
  )

export const uniqueId = () => Math.random().toString(16).slice(2, 10)
