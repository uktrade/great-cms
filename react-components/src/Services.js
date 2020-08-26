/* eslint-disable */
import { createStore } from 'redux'

import reducers from '@src/reducers'
import actions from '@src/actions'

const MESSAGE_UNEXPECTED_ERROR = { __all__: ['Unexpected Error'] }
const MESSAGE_PERMISSION_DENIED = { __all__: ['You do not have permission to perform this action'] }
const MESSAGE_NOT_FOUND_ERROR = { __all__: ['Not found'] }
const MESSAGE_TIMEOUT_ERROR = { __all__: ['Request timed out'] }
const MESSAGE_BAD_REQUEST_ERROR = { __all__: ['Bad request'] }

export const store = createStore(reducers)

const setInitialState = function(state) {
  store.dispatch(actions.setInitialState(state))
}

const post = function(url, data) {
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

const httpDelete = function (url, data) {
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

const get = function (url, params) {
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

const getCountriesDataBySectors = function(sectors) {
  return get(config.countriesBySectorsDataUrl, { sectors: sectors }).then((response) =>
    responseHandler(response).json()
  )
}

const getCountryData = function(country) {
  return get(config.countryDataUrl, { country: country }).then((response) => responseHandler(response).json())
}

const getMarketingCountryData = function(data) {
  return get(config.marketingCountryData, data).then((response) => responseHandler(response).json())
}

const removeSector = function() {
  return get(config.removeSectorUrl, {}).then((response) => responseHandler(response).json())
}

const removeCountryData = function(country) {
  return get(config.removeCountryDataUrl, { country: country }).then((response) => responseHandler(response).json())
}

const lookupProduct = function({ q }) {
  return get(config.apiLookupProductUrl, { q }).then((response) => responseHandler(response).json())
}

const createUser = function({ email, password }) {
  return post(config.apiSignupUrl, { email, password }).then(responseHandler)
}

const updateExportPlan = function(data) {
  return post(config.apiUpdateExportPlanUrl, data).then(responseHandler)
}

const createObjective = function (data) {
  return post(config.apiObjectivesCreateUrl, data).then(responseHandler)
}

const deleteObjective = function (pk) {
  return httpDelete(config.apiObjectivesDeleteUrl, {pk: pk}).then(responseHandler)
}

const updateObjective = function (data) {
  return post(config.apiObjectivesUpdateUrl, data).then(responseHandler)
}

const checkVerificationCode = function ({ email, code }) {
  return post(config.verifyCodeUrl, { email, code }).then(responseHandler)
}

const checkCredentials = function({ email, password }) {
  return post(config.apiLoginUrl, { email, password }).then(responseHandler)
}

const updateCompany = function({ company_name, expertise_industries, expertise_countries, first_name, last_name }) {
  const data = {
    company_name,
    expertise_industries,
    expertise_countries,
    first_name,
    last_name
  }
  return post(config.apiUpdateCompanyUrl, data).then(responseHandler)
}

const getLessonComplete = function(endpoint) {
  return get(endpoint).then(responseHandler)
}

const setLessonComplete = function(endpoint) {
  return post(endpoint).then(responseHandler)
}

const setLessonIncomplete = function(endpoint) {
  return httpDelete(endpoint).then(responseHandler)
}

const createRouteToMarket = function (data) {
  return post(config.apiRouteToMarketCreateUrl, data).then((response) => responseHandler(response).json())
}

const deleteRouteToMarket = function (pk) {
  return httpDelete(config.apiRouteToMarketDeleteUrl, {pk: pk}).then(responseHandler)
}

const updateRouteToMarket = function (data) {
  return post(config.apiRouteToMarketUpdateUrl, data).then((response) => responseHandler(response).json())
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

// static values that will not change during execution of the code
let config = {}
const setConfig = function({
  countryDataUrl,
  marketingCountryData,
  removeSectorUrl,
  removeCountryDataUrl,
  countriesBySectorsDataUrl,
  apiLoginUrl,
  apiSignupUrl,
  apiLookupProductUrl,
  apiUpdateCompanyUrl,
  countryOptions,
  csrfToken,
  dashboardUrl,
  googleUrl,
  industryOptions,
  linkedInUrl,
  loginUrl,
  passwordResetUrl,
  termsUrl,
  verifyCodeUrl,
  userIsAuthenticated,
  apiUpdateExportPlanUrl,
  apiObjectivesCreateUrl,
  apiObjectivesDeleteUrl,
  apiObjectivesUpdateUrl,
  apiRouteToMarketCreateUrl,
  apiRouteToMarketDeleteUrl,
  apiRouteToMarketUpdateUrl,
  exportPlanTargetMarketsUrl,
  signupUrl
}) {
  config.countryDataUrl = countryDataUrl
  config.marketingCountryData = marketingCountryData
  config.removeSectorUrl = removeSectorUrl
  config.removeCountryDataUrl = removeCountryDataUrl
  config.countriesBySectorsDataUrl = countriesBySectorsDataUrl
  config.apiLoginUrl = apiLoginUrl
  config.apiSignupUrl = apiSignupUrl
  config.apiLookupProductUrl = apiLookupProductUrl
  config.apiUpdateCompanyUrl = apiUpdateCompanyUrl
  config.apiUpdateExportPlanUrl = apiUpdateExportPlanUrl
  config.apiObjectivesCreateUrl = apiObjectivesCreateUrl
  config.apiObjectivesDeleteUrl = apiObjectivesDeleteUrl
  config.apiObjectivesUpdateUrl = apiObjectivesUpdateUrl
  config.apiRouteToMarketCreateUrl = apiRouteToMarketCreateUrl
  config.apiRouteToMarketDeleteUrl = apiRouteToMarketDeleteUrl
  config.apiRouteToMarketUpdateUrl = apiRouteToMarketUpdateUrl
  config.countryOptions = countryOptions
  config.csrfToken = csrfToken
  config.dashboardUrl = dashboardUrl
  config.googleUrl = googleUrl
  config.industryOptions = industryOptions
  config.linkedInUrl = linkedInUrl
  config.loginUrl = loginUrl
  config.passwordResetUrl = passwordResetUrl
  config.termsUrl = termsUrl
  config.verifyCodeUrl = verifyCodeUrl
  config.userIsAuthenticated = userIsAuthenticated
  config.exportPlanTargetMarketsUrl = exportPlanTargetMarketsUrl
  config.signupUrl = signupUrl
}

export default {
  createUser,
  checkCredentials,
  checkVerificationCode,
  get,
  store: store,
  updateCompany,
  getCountryData,
  getMarketingCountryData,
  removeCountryData,
  removeSector,
  getCountriesDataBySectors,
  updateExportPlan,
  createObjective,
  deleteObjective,
  updateObjective,
  lookupProduct,
  setConfig,
  getLessonComplete,
  setLessonComplete,
  setLessonIncomplete,
  config,
  createRouteToMarket,
  deleteRouteToMarket,
  updateRouteToMarket,
  setInitialState,
  messages: {
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_PERMISSION_DENIED,
    MESSAGE_NOT_FOUND_ERROR,
    MESSAGE_TIMEOUT_ERROR
  }
}
