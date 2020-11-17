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
/* Unused 
const getCountriesDataBySectors = function(sectors) {
  return api.get(config.countriesBySectorsDataUrl, { sectors: sectors }).then((response) =>
    api.responseHandler(response).json()
  )
}

const removeSector = function() {
  return api.get(config.removeSectorUrl, {}).then((response) => api.responseHandler(response).json())
}

const removeCountryData = function(country) {
  return api.get(config.removeCountryDataUrl, { country: country }).then((response) => api.responseHandler(response).json())
}
*/

export default Object.assign({},api,{
  store: store,
  config,
  setConfig,
  setInitialState,
})
