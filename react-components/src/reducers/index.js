import api from '@src/api'
import { get } from '@src/Helpers'
import {
  SET_MODAL_IS_OPEN,
  SET_INITIAL_STATE,
  SET_PRODUCTS_EXPERTISE,
  SET_COUNTRIES_EXPERTISE,
  SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
  SET_NEXT_URL,
  SET_PRODUCT,
  SET_MARKET,
  SET_LOADED,
  SET_COMPARISON_MARKETS,
} from '@src/actions'
import { config } from '@src/config'
import { combineReducers } from 'redux'
import costAndPricing from '@src/reducers/costsAndPricing'

const saveToExportPlan = (payload) => {
  return api.updateExportPlan(payload).catch(() => {
    // TODO: Add error confirmation here
  })
}

const saveToUserProducts = (payload) => {
  return api.addUpdateProduct(payload).catch(() => {
    // TODO: Add error confirmation here
  })
}

const saveToUserMarkets = (payload) => {
  return api.addUpdateMarket(payload).catch(() => {
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



const userBasketReducer = (state, action) => {
  const newState = { ...state }
  let codeChanged
  switch (action.type) {
    case SET_PRODUCT:
      codeChanged =
        (newState.products &&
          newState.products[0] &&
          newState.products[0].commodity_code) !== action.payload.commodity_code
      newState.products = [action.payload]

      saveToUserProducts(action.payload).then(
        () => {
          if (codeChanged && config.refreshOnMarketChange) {
            api.reloadPage()
          }
        }
      )
      break
    case SET_MARKET:
      newState.markets = [action.payload]
      saveToUserMarkets(action.payload).then(() => {
        if (config.refreshOnMarketChange) {
          api.reloadPage()
        }
      })
      break
    default:
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

const comparisonMarkets = (state, action) => {
  const newState = { ...state }
  if (action.type === SET_COMPARISON_MARKETS) {
    newState.comparisonMarkets = action.payload
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

export const getProducts = (state) => ((state.userBasket && state.userBasket.products) || [])[0]
export const getMarkets = (state) => ((state.userBasket && state.userBasket.markets) || [])[0]

export const getCacheVersion = (state) =>
  state.dataLoader && state.dataLoader.cacheVersion
export const getComparisonMarkets = (state) => state.comparisonMarkets || []

const rootReducer = (state, action) => {
  let localState = baseReducers(state, action)
  localState = setInitialStateReducer(localState, action)
  return combineReducers({
    userBasket: userBasketReducer,
    modalIsOpen: setModalIsOpen,
    dataLoader: dataCacheReducer,
    comparisonMarkets,
    costAndPricing,
  })(localState, action)
}

export default rootReducer
