import {
  updateField,
  postField,
  UPDATE_FIELD,
  FIELD_UPDATE_SUCCESS,
  FIELD_UPDATE_FAIL,
} from '.'
import Api from '@src/api'

const dispatch = jest.fn()

describe('Costs and Pricing Actions', () => {
  describe('updateField', () => {
    const field = { product: 'tea' }
    it('Should return updated field', () => {
      expect(updateField(field)).toEqual({
        type: UPDATE_FIELD,
        payload: field,
      })
    })
  })

  describe('postField', () => {
    it('Should successfully post', async () => {
      const resolved = { calculated_cost_pricing: 0.0 }
      Api.updateCalculateCostAndPricing = jest.fn(() =>
        Promise.resolve(resolved)
      )
      await postField({ direct_costs: { product_costs: 5 } })(dispatch)
      expect(dispatch).toHaveBeenCalledWith({
        type: FIELD_UPDATE_SUCCESS,
        data: resolved,
      })
    })

    it('Should fail request', async () => {
      const err = { response: { status: 400 } }
      Api.updateCalculateCostAndPricing = jest.fn(() => Promise.reject(err))
      await postField({ direct_costs: { product_costs: 5 } })(dispatch)
      expect(dispatch).toHaveBeenCalledWith({ type: FIELD_UPDATE_FAIL, err })
    })
  })
})
