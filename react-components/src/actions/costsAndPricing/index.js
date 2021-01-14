import Api from '@src/api'

export const UPDATE_FIELD = 'UPDATE_FIELD'
export const FIELD_UPDATE_SUCCESS = 'FIELD_UPDATE_SUCCESS'
export const FIELD_UPDATE_FAIL = 'FIELD_UPDATE_FAIL'
export const INIT_COST_PRICING = 'INIT_COST_PRICING'

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
