import reducer, { initialState } from '.'
import { updateField, postSuccess } from '@src/actions/costsAndPricing'

describe('Costs and Pricing Reducer', () => {
  it('Should have initial state', () => {
    expect(reducer(undefined, { type: '@@INIT' })).toEqual(initialState)
  })

  it('Should return updated field state', () => {
    const field = { product_costs: 4 }
    expect(reducer(initialState, updateField(field))).toEqual({
      ...initialState,
      product_costs: 4,
    })
  })

  it('Should return updated cost and pricing state', () => {
    expect(
      reducer(
        initialState,
        postSuccess({
          calculated_cost_pricing: {
            total_direct_costs: 5,
            total_overhead_costs: 10,
            profit_per_unit: 2,
            potential_total_profit: 4,
            gross_price_per_unit: 1,
          },
        })
      )
    ).toEqual({
      ...initialState,
      direct_total: 5,
      overhead_total: 10,
      profit_per_unit: 2,
      potential_total_profit: 4,
      gross_price_per_unit: 1,
    })
  })
})
