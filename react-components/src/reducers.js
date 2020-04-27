import {
  SET_MODAL_IS_OPEN,
  SET_INITIAL_STATE,
  SET_PRODUCTS_EXPERTISE,
  SET_COUNTRIES_EXPERTISE,
  SET_PERFORM_FEATURE_SKIP_COOKIE_CHECK,
  SET_NEXT_URL,
} from '@src/actions'

const initialState = {
  // prevents modals from opening on page load if user dismissed the modal already
  performSkipFeatureCookieCheck: true,
  // place to send user on successful completion of certain forms
  nextUrl: undefined,
  modalIsOpen: {
    products: false,
    countries: false,
    industries: false,
    login: false,
    signup: false,
  },
  user: {
    expertise: {
      countries: [],
      industries: [],
      products: [],
    }
  },
}

 
// todo: replace with ImmutableJS
const cloneState = state => JSON.parse(JSON.stringify(state))

function setModalIsOpen(state, payload) {
  let newState = cloneState(state)
  // should have only one modal open at a time
  newState.modalIsOpen ={
    products: false,
    countries: false,
    industries: false,
    login: false,
    signup: false,
  }
  newState.modalIsOpen[payload.modalID] = payload.isOpen
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

function setInitialState(state, {modalIsOpen, user}) {
  let newState = cloneState(state)
  Object.assign(newState.modalIsOpen, modalIsOpen)
  Object.assign(newState.user, user)
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


export default function rootReducer(state = initialState, action) {
  switch (action.type) {
    case SET_INITIAL_STATE:
      return setInitialState(state, action.payload)
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


export const getModalIsOpen = (state, name) => state.modalIsOpen[name]
export const getCountriesExpertise = state => state.user.expertise.countries
export const getProductsExpertise = state => state.user.expertise.products
export const getIndustriesExpertise = state => state.user.expertise.industries
export const getPerformFeatureSKipCookieCheck = state => state.performSkipFeatureCookieCheck
export const getNextUrl = state => state.nextUrl
