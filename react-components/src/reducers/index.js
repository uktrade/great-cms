import api from '@src/api'
import { analytics } from '@src/Helpers'
import {
  SET_MODAL_IS_OPEN,
  SET_INITIAL_STATE,
  SET_PRODUCTS_EXPERTISE,
  SET_COUNTRIES_EXPERTISE,
  SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
  SET_NEXT_URL,
  SET_PRODUCT,
  SET_MARKET,
} from '@src/actions'
import { config } from '@src/config'
import { combineReducers, reduceReducers } from 'redux'
import costAndPricing from '@src/reducers/costsAndPricing'


const saveToExportPlan = (payload) => {
  api.updateExportPlan(payload).catch(() => {
      // TODO: Add error confirmation here
    })
}

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

//const cloneState = state => JSON.parse(JSON.stringify(state))

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
  let newState = cloneState(state)
  newState.user.expertise.products = payload
  return newState
}

function setCountriesExpertise(state, payload) {
  let newState = cloneState(state)
  newState.user.expertise.countries = payload
  return newState
}

function setPerformFeatureSKipCookieCheck(state, payload) {
  let newState = cloneState(state)
  newState.performSkipFeatureCookieCheck = payload
  return newState
}

function setNextUrl(state, payload) {
  let newState = cloneState(state)
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

const exportPlanReducer = (state, action) => {
  let newState = Object.assign({}, state)
  switch (action.type) {
    case SET_PRODUCT:
      saveToExportPlan({export_commodity_codes:[action.payload]})
      const codeChanged = newState.products && (newState.products[0] && (newState.products[0].commodity_code != action.payload.commodity_code))
      newState.products = [action.payload]
      if (codeChanged && config.refreshOnMarketChange) {
        window.location.reload()
      }
      break
    case SET_MARKET:
      saveToExportPlan({export_countries:[action.payload]})
      newState.markets = [action.payload]
      if (config.refreshOnMarketChange) {
        window.location.reload()
      }
  }
  return newState
}

const setInitialStateReducer = (state, action) => {
  if (action.type === SET_INITIAL_STATE) {
    state = action.payload
  }
  return state
}

export const getModalIsOpen = (state, name) => state.modalIsOpen[name]
export const getCountriesExpertise = state => state.user && state.user.expertise && state.user.expertise.countries
export const getProductsExpertise = state => state.user && state.user.expertise && state.user.expertise.products
export const getIndustriesExpertise = state => state.user && state.user.expertise && state.user.expertise.industries
export const getPerformFeatureSKipCookieCheck = state => state.performSkipFeatureCookieCheck
export const getNextUrl = state => state.nextUrl

export const getProducts = state => ((state.exportPlan && state.exportPlan.products) || [])[0]
export const getMarkets = state => ((state.exportPlan && state.exportPlan.markets) || [])[0]

const rootReducer = (state, action) => {
  state = baseReducers(state, action)
  state = setInitialStateReducer(state, action)
  return combineReducers({ exportPlan: exportPlanReducer, modalIsOpen: setModalIsOpen, costAndPricing })(state, action)
}

export default rootReducer
