import Api from '@src/api'
import { isObject } from '@src/Helpers'

export const UPDATE_FIELD = 'UPDATE_FIELD'
export const FIELD_UPDATE_SUCCESS = 'FIELD_UPDATE_SUCCESS'
export const FIELD_UPDATE_FAIL = 'FIELD_UPDATE_FAIL'
export const INIT_COST_PRICING = 'INIT_COST_PRICING'

const waitTime = 2000

export const updateField = (payload) => ({
  type: UPDATE_FIELD,
  payload,
})

export const init = (payload) => ({
  type: INIT_COST_PRICING,
  payload,
})

export const postSuccess = (payload) => ({
  type: FIELD_UPDATE_SUCCESS,
  payload,
})

export const postFail = (err) => ({ type: FIELD_UPDATE_FAIL, err })

export const postField = (field) => async (dispatch) => {
  await Api.updateCalculateCostAndPricing(field)
    .then((data) => {
      dispatch(postSuccess(data))
    })
    .catch((err) => {
      dispatch(postFail(err))
    })
}

const getKeyFromField = (field) => {
  // Generates a key from the provided field, so we know whether to cancel the in-flight update
  if (isObject(field)) {
    const key = Object.keys(field)[0]
    return key + ':' + getKeyFromField(field[key])
  }
  return ''
}

const debounce = (() => {
  let timeout = null
  let lastKey = null
  return (field, dispatch) => {
    const key = getKeyFromField(field)
    if (timeout && lastKey === key) clearTimeout(timeout)
    lastKey = key
    timeout = setTimeout(() => {
      timeout = null
      dispatch(postField(field))
    }, waitTime)
  }
})()

export const debouncePostField = (() => {
  return (field) => (dispatch) => {
    debounce(field, dispatch)
  }
})()
