import Api from '@src/api'

export const UPDATE_FIELD = 'UPDATE_FIELD'
export const FIELD_UPDATE_SUCCESS = 'FIELD_UPDATE_SUCCESS'
export const FIELD_UPDATE_FAIL = 'FIELD_UPDATE_FAIL'

export const updateField = (payload) => ({
  type: UPDATE_FIELD,
  payload,
})

export const postField = (field) => async (dispatch) => {
  await Api.updateCalculateCostAndPricing(field)
    .then((data) => {
      dispatch({ type: FIELD_UPDATE_SUCCESS, data })
    })
    .catch((err) => {
      dispatch({ type: FIELD_UPDATE_FAIL, err })
    })
}
