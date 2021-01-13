import reducer, { initialState } from '.'
import { updateField, postSuccess } from '@src/actions/costsAndPricing'

describe('Costs and Pricing Reducer', () => {
  it('Should have initial state', () => {
    expect(reducer(undefined, { type: '@@INIT' })).toEqual(initialState)
  })

  it('Should return updated field state', () => {
    const field = { product: 'tea' }
    expect(reducer(initialState, updateField(field))).toEqual({
      ...initialState,
      ...field,
    })
  })

  it('Should return updated cost and pricing state', () => {
    expect(
      reducer(initialState, postSuccess({ calculated_cost_pricing: 0.0 }))
    ).toEqual({
      ...initialState,
    })
  })
})
