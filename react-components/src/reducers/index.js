import api from '@src/api'

import {
  SET_MODAL_IS_OPEN,
  SET_INITIAL_STATE,
  SET_PRODUCTS_EXPERTISE,
  SET_COUNTRIES_EXPERTISE,
  SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
  SET_NEXT_URL,
  SET_EP_PRODUCT,
  SET_EP_MARKET,
  SET_LOADED,
  SET_USER_SETTING,
} from '@src/actions'
import { config } from '@src/config'
import { combineReducers } from 'redux'
import costAndPricing from '@src/reducers/costsAndPricing'

const initialState = {
  // prevents modals from opening on page load if user dismissed the modal already
  modalIsOpen: {
    products: false,
    countries: false,
    industries: false,
    login: false,
    signup: false,
  },
}

const cloneState = (state) => JSON.parse(JSON.stringify(state))

function setModalIsOpen(state, payload) {
  // should have only one modal open at a time
  const newState = {
    products: false,
    countries: false,
    industries: false,
    login: false,
    signup: false,
  }
  newState[payload.modalID] = payload.isOpen
  return newState
}

function setProductsExpertise(state, payload) {
  const newState = cloneState(state)
  newState.user.expertise.products = payload
  return newState
}

function setCountriesExpertise(state, payload) {
  const newState = cloneState(state)
  newState.user.expertise.countries = payload
  return newState
}

function setPerformFeatureSKipCookieCheck(state, payload) {
  const newState = cloneState(state)
  newState.performSkipFeatureCookieCheck = payload
  return newState
}

function setNextUrl(state, payload) {
  const newState = cloneState(state)
  newState.nextUrl = payload
  return newState
}

const baseReducers = (state = initialState, action) => {
  switch (action.type) {
    case SET_MODAL_IS_OPEN:
      return setModalIsOpen(state, action.payload)
    case SET_PRODUCTS_EXPERTISE:
      return setProductsExpertise(state, action.payload)
    case SET_COUNTRIES_EXPERTISE:
      return setCountriesExpertise(state, action.payload)
    case SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK:
      return setPerformFeatureSKipCookieCheck(state, action.payload)
    case SET_NEXT_URL:
      return setNextUrl(state, action.payload)
    default:
      return state
  }
}

const userSettingsReducer = (state, action) => {
  const newState = { ...state }
  switch (action.type) {
    case SET_USER_SETTING:
      const name = action.payload.name
      if(newState[name]) {
        api.setUserData(name, action.payload.value).then(() => {
          if (config.refreshOnMarketChange) {
            api.reloadPage()
          }
        })
      }
      newState[name] = action.payload.value
      break
    default:
  }
  return newState
}

const exportPlanReducer = (state, action) => {
    const newState = { ...state }
    switch (action.type) {
      case SET_EP_PRODUCT:
        newState.product = action.payload
        break
      case SET_EP_MARKET:
        newState.market = action.payload
        break
    }
  return newState
}

const dataCacheReducer = (state, action) => {
  const newState = { ...state }
  if (action.type === SET_LOADED) {
    newState.cacheVersion = (newState.cacheVersion || 0) + 1
    return newState
  }
  return newState
}

const setInitialStateReducer = (state, action) => {
  if (action.type === SET_INITIAL_STATE) {
    return action.payload
  }
  return state
}

export const getModalIsOpen = (state, name) => state.modalIsOpen[name]
export const getCountriesExpertise = (state) =>
  state.user && state.user.expertise && state.user.expertise.countries
export const getProductsExpertise = (state) =>
  state.user && state.user.expertise && state.user.expertise.products
export const getIndustriesExpertise = (state) =>
  state.user && state.user.expertise && state.user.expertise.industries
export const getPerformFeatureSKipCookieCheck = (state) =>
  state.performSkipFeatureCookieCheck
export const getNextUrl = (state) => state.nextUrl

// Export plan contains single product and market
export const getEpProduct = (state) =>
  state.exportPlan && state.exportPlan.product
export const getEpMarket = (state) =>
  state.exportPlan && state.exportPlan.market

export const getCacheVersion = (state) =>
  state.dataLoader && state.dataLoader.cacheVersion

const rootReducer = (state, action) => {
  let localState = baseReducers(state, action)
  localState = setInitialStateReducer(localState, action)
  return combineReducers({
    userSettings: userSettingsReducer,
    exportPlan: exportPlanReducer,
    modalIsOpen: setModalIsOpen,
    dataLoader: dataCacheReducer,
    costAndPricing,
  })(localState, action)
}

export default rootReducer
