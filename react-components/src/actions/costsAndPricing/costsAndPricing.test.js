import {
  updateField,
  postField,
  init,
  postSuccess,
  UPDATE_FIELD,
  FIELD_UPDATE_SUCCESS,
  FIELD_UPDATE_FAIL,
  INIT_COST_PRICING,
} from '.'
import Api from '@src/api'

const dispatch = jest.fn()
const field = { labour_costs: 4 }

describe('Costs and Pricing Actions', () => {
  describe('updateField', () => {
    it('Should return updated field', () => {
      expect(updateField(field)).toEqual({
        type: UPDATE_FIELD,
        payload: field,
      })
    })
  })

  describe('init', () => {
    it('Should initialise action', () => {
      expect(init(field)).toEqual({
        type: INIT_COST_PRICING,
        payload: field,
      })
    })
  })

  describe('postSuccess', () => {
    it('Should return successful state', () => {
      expect(postSuccess(field)).toEqual({
        type: FIELD_UPDATE_SUCCESS,
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
        payload: resolved,
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
