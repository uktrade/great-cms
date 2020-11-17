/* eslint-disable */
import { config } from '@src/config'

const MESSAGE_UNEXPECTED_ERROR = { __all__: ['Unexpected Error'] }
const MESSAGE_PERMISSION_DENIED = { __all__: ['You do not have permission to perform this action'] }
const MESSAGE_NOT_FOUND_ERROR = { __all__: ['Not found'] }
const MESSAGE_TIMEOUT_ERROR = { __all__: ['Request timed out'] }
const MESSAGE_BAD_REQUEST_ERROR = { __all__: ['Bad request'] }

const post = function(url, data) {
      console.log('******************* post', url)
  return fetch(url, {
    method: 'post',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify(data)
  })
}

const httpDelete = function(url, data) {
  return fetch(url, {
    method: 'delete',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  })
}

const get = function(url, params) {
  const parsedUrl = new URL(`${location.origin}${url}`)
  const parsedParams = new URLSearchParams(params).toString()
  parsedUrl.search = parsedParams

  return fetch(parsedUrl, {
    method: 'get',
    headers: {
      Accept: 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
}

const responseHandler = function(response) {
  if (response.status == 400) {
    return response.json().then((error) => {
      throw error
    })
  } else if (response.status == 403) {
    throw MESSAGE_PERMISSION_DENIED
  } else if (response.status == 404) {
    throw MESSAGE_NOT_FOUND_ERROR
  } else if (response.status == 504) {
    throw MESSAGE_TIMEOUT_ERROR
  } else if (response.status == 400) {
    throw MESSAGE_BAD_REQUEST_ERROR
  } else if (response.status != 200) {
    throw MESSAGE_UNEXPECTED_ERROR
  } else {
    return response
  }
}

export default {
  responseHandler,

  checkCredentials: ({ email, password }) => {
    return post(config.apiLoginUrl, { email, password }).then(responseHandler)
  },

  logout: () => {
    return post(config.apiLogoutUrl).then(responseHandler)
  },

  updateExportPlan: (data) => {
    return post(config.apiUpdateExportPlanUrl, data).then(responseHandler)
  },

  getCountries: () => {
    return get(config.apiCountriesUrl, {}).then((response) => responseHandler(response).json())
  },

  getSuggestedCountries: (hs_code) => {
    return get(config.apiSuggestedCountriesUrl, { hs_code }).then((response) => responseHandler(response).json())
  },

  getCountryData: (country) => {
    return get(config.countryDataUrl, { country: country }).then((response) => responseHandler(response).json())
  },

  getPopulationByCountryData: (countries) => {
    return get(config.populationByCountryUrl, { countries: countries }).then((response) => responseHandler(response).json())
  },

  getMarketingCountryData: (data) => {
    return get(config.marketingCountryData, data).then((response) => responseHandler(response).json())
  },

  lookupProduct: ({ proddesc }) => {
    return post(config.apiLookupProductUrl, { proddesc }).then((response) => responseHandler(response).json())
  },

  lookupProductRefine: ({ txId, interactionId, values }) => {
    return post(config.apiLookupProductUrl, { tx_id: txId, interaction_id: interactionId, values: values }).then((response) => responseHandler(response).json())
  },

  getLessonComplete: (endpoint) => {
    return get(endpoint).then(responseHandler)
  },

  setLessonComplete: (endpoint) => {
    return post(endpoint).then(responseHandler)
  },

  setLessonIncomplete: (endpoint) => {
    return httpDelete(endpoint).then(responseHandler)
  },

  createRouteToMarket: (data) => {
    return post(config.apiRouteToMarketCreateUrl, data).then((response) => responseHandler(response).json())
  },

  deleteRouteToMarket: (pk) => {
    return httpDelete(config.apiRouteToMarketDeleteUrl, { pk: pk }).then(responseHandler)
  },

  updateRouteToMarket: (data) => {
    return post(config.apiRouteToMarketUpdateUrl, data).then((response) => responseHandler(response).json())
  },

  createObjective: (data) => {
    return post(config.apiObjectivesCreateUrl, data).then(responseHandler)
  },

  deleteObjective: (pk) => {
    return httpDelete(config.apiObjectivesDeleteUrl, { pk: pk }).then(responseHandler)
  },

  updateObjective: (data) => {
    return post(config.apiObjectivesUpdateUrl, data).then(responseHandler)
  },
  messages: {
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_PERMISSION_DENIED,
    MESSAGE_NOT_FOUND_ERROR,
    MESSAGE_TIMEOUT_ERROR
  }
}
