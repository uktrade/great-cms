import Services from '@src/Services'
import { analytics } from '@src/Helpers'

const saveToExportPlan = (country) => {
  Services.updateExportPlan({
      export_countries: [country]
    })
    .then(() => {
      closeModal()
      window.location.reload()
    })
    .then(
      analytics({
        'event': 'addMarketSuccess',
        'suggestMarket': country.suggested ? country.name : '',
        'listMarket': country.suggested ? '' : country.name,
        'marketAdded': country.name
      })
    )
    .catch(() => {
      // TODO: Add error confirmation here
    })
}


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
import { combineReducers, reduceReducers } from 'redux'

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
  products: [],
  markets: [],
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


const exportPlanReducer = (state, action) => {
  let newState = Object.assign({}, state);
  switch (action.type) {
    case SET_PRODUCT:
      newState.products = [action.payload]
      break
    case SET_MARKET:
      console.log('Set market', newState.markets && newState.markets[0], action.payload)
      saveToExportPlan(action.payload)
      //let newMarket = {country_name:action.payload.name}
      newState.markets = [action.payload]
  }
  return newState
}

const setInitialStateReducer = (state, action) => {
  if(action.type === SET_INITIAL_STATE) {
    console.log('set initial sate ***** ', action.payload)
    state = action.payload
  }
  return state
}

export const getModalIsOpen = (state, name) => state.modalIsOpen[name]
export const getCountriesExpertise = state => state.user.expertise.countries
export const getProductsExpertise = state => state.user.expertise.products
export const getIndustriesExpertise = state => state.user.expertise.industries
export const getPerformFeatureSKipCookieCheck = state => state.performSkipFeatureCookieCheck
export const getNextUrl = state => state.nextUrl

export const getProducts = state => ((state.exportPlan && state.exportPlan.products) || [])[0]
export const getMarkets = state => ((state.exportPlan && state.exportPlan.markets) || [])[0]

const rootReducer = (state, action) => {
  const state1 = setInitialStateReducer(state, action)
  return combineReducers({exportPlan: exportPlanReducer, modalIsOpen: setModalIsOpen})(state1, action)
} 

export default rootReducer

