import Api from '@src/api'

export const UPDATE_FIELD = 'UPDATE_FIELD'

export const updateField = (payload) => ({
  type: UPDATE_FIELD,
  payload,
})

export const postField = (payload) => async (dispatch) => {
  await Api.updateCalculateCostAndPricing(payload)
    .then(({ data }) => {
      dispatch({ type: 'Success', data })
    })
    .catch(({ response }) => {
      dispatch({ type: 'fail', response })
    })
}
