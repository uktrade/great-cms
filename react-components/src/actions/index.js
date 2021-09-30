// action types

export const SET_MODAL_IS_OPEN = 'SET_MODAL_IS_OPEN'
export const SET_PRODUCTS_EXPERTISE = 'SET_PRODUCTS_EXPERTISE'
export const SET_COUNTRIES_EXPERTISE = 'SET_COUNTRIES_EXPERTISE'
export const SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK =
  'SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK'
export const SET_NEXT_URL = 'SET_NEXT_URL'
export const SET_INITIAL_STATE = 'SET_INITIAL_STATE'
export const SET_LOADED = 'SET_LOADED'
export const SET_EP_PRODUCT = 'SET_EP_PRODUCT'
export const SET_EP_MARKET = 'SET_EP_MARKET'
export const SET_USER_SETTING = 'SET_USER_SETTING'

// action creators

const setProductsExpertise = (payload) => ({
  type: SET_PRODUCTS_EXPERTISE,
  payload,
})

const setCountriesExpertise = (payload) => ({
  type: SET_COUNTRIES_EXPERTISE,
  payload,
})

const toggleModalIsOpen = (modalID, isOpen) => ({
  type: SET_MODAL_IS_OPEN,
  payload: { modalID, isOpen },
})

const skipFeatureCookieCheck = () => ({
  type: SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
  payload: false,
})

const setNextUrl = (nextUrl) => ({
  type: SET_NEXT_URL,
  payload: nextUrl,
})

const setInitialState = (payload) => ({
  type: SET_INITIAL_STATE,
  payload,
})

const setEpProduct = (product) => ({
  type: SET_EP_PRODUCT,
  payload: product,
})

const setEpMarket = (market) => ({
  type: SET_EP_MARKET,
  payload: market,
})

const setLoaded = () => ({
  type: SET_LOADED,
})

const setUserData = (blobName, value) => ({
  type: SET_USER_SETTING,
  payload: { name: blobName, value },
})

export default {
  toggleModalIsOpen,
  setProductsExpertise,
  setCountriesExpertise,
  skipFeatureCookieCheck,
  setNextUrl,
  setInitialState,
  setEpProduct,
  setEpMarket,
  setLoaded,
  setUserData,
}
