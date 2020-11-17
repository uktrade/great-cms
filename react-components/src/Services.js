/* eslint-disable */
import { createStore } from 'redux'
import { config, setConfig } from '@src/config'

import reducers from '@src/reducers'
import actions from '@src/actions'
import api from '@src/api'

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

const getCountriesDataBySectors = function(sectors) {
  return get(config.countriesBySectorsDataUrl, { sectors: sectors }).then((response) =>
    api.responseHandler(response).json()
  )
}

const removeSector = function() {
  return get(config.removeSectorUrl, {}).then((response) => api.responseHandler(response).json())
}

const removeCountryData = function(country) {
  return get(config.removeCountryDataUrl, { country: country }).then((response) => api.responseHandler(response).json())
}

const createUser = function({ email, password }) {
  return post(config.apiSignupUrl, { email, password }).then(api.responseHandler)
}

const checkVerificationCode = function({ email, code }) {
  return post(config.verifyCodeUrl, { email, code }).then(api.responseHandler)
}

const updateCompany = function({ company_name, expertise_industries, expertise_countries, first_name, last_name }) {
  const data = {
    company_name,
    expertise_industries,
    expertise_countries,
    first_name,
    last_name
  }
  return post(config.apiUpdateCompanyUrl, data).then(api.responseHandler)
}


export default Object.assign({},api,{
  createUser,
  checkVerificationCode,
  get,
  store: store,
  updateCompany,
  removeCountryData,
  removeSector,
  getCountriesDataBySectors,
  config,
  setConfig,
  setInitialState,
})
