// action types

export const SET_MODAL_IS_OPEN = 'SET_MODAL_IS_OPEN'
export const SET_PRODUCTS_EXPERTISE = 'SET_PRODUCTS_EXPERTISE'
export const SET_COUNTRIES_EXPERTISE = 'SET_COUNTRIES_EXPERTISE'
export const SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK = 'SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK'
export const SET_NEXT_URL = 'SET_NEXT_URL'
export const SET_INITIAL_STATE = 'SET_INITIAL_STATE'
export const SET_PRODUCT = 'SET_PRODUCT'
export const SET_MARKET = 'SET_MARKET'

// action creators

const setProductsExpertise = function(payload) {
  return {
    type: SET_PRODUCTS_EXPERTISE,
    payload: payload,
  }
}


const setCountriesExpertise = function(payload) {
  return {
    type: SET_COUNTRIES_EXPERTISE,
    payload: payload,
  }
}


const toggleModalIsOpen = function(modalID, isOpen) {
  return {
    type: SET_MODAL_IS_OPEN,
    payload: {modalID, isOpen},
  }
}


const skipFeatureCookieCheck = function() {
  return {
    type: SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
    payload: false,
  }
}

const setNextUrl = function(nextUrl) {
  return {
    type: SET_NEXT_URL,
    payload: nextUrl,
  }
}

const setInitialState = function(payload) {
  console.log('In set intitial state action payload:', payload)
  return {
    type: SET_INITIAL_STATE,
    payload: payload,
  }
}

const setProduct = function(product) {
  return {
    type: SET_PRODUCT,
    payload: product
  }
}

const setMarket = function(market) {
  return {
    type: SET_MARKET,
    payload: market
  }
}

export default {
  toggleModalIsOpen,
  setProductsExpertise,
  setCountriesExpertise,
  skipFeatureCookieCheck,
  setNextUrl,
  setInitialState,
  setProduct,
  setMarket,
}
