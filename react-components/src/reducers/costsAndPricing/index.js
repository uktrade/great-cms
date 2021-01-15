import {
  UPDATE_FIELD,
  FIELD_UPDATE_SUCCESS,
  INIT_COST_PRICING,
} from '@src/actions/costsAndPricing'

export const initialState = {
  product_costs: '',
  labour_costs: '',
  other_direct_costs: '',
  product_adaption: '',
  packaging: '',
  freight_logistics: '',
  agent_distributor_fees: '',
  marketing: '',
  insurance: '',
  other_overhead_costs: '',
  direct_total: '0.00',
  overhead_total: '0.00',
  cost_per_unit: '',
  average_price: '',
  net_price: '',
  local_taxes: '',
  duty: '',
  gross_price_per_unit: '0',
  potential_per_unit: '0',
  gross_price_per_unit_invoicing: '',
  gross_price_per_unit_currency: '',
  profit_per_unit: '0',
  price_per_unit: '',
  units_to_export: '',
  export_units: '',
  time_frame: '',
  export_time_frame: '',
}

export default (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_FIELD: {
      return { ...state, ...action.payload }
    }
    case INIT_COST_PRICING: {
      const {
        calculated_cost_pricing,
        direct_costs,
        overhead_costs,
      } = action.payload
      return {
        ...state,
        ...direct_costs,
        ...overhead_costs,
        direct_total: calculated_cost_pricing.total_direct_costs,
        overhead_total: calculated_cost_pricing.total_overhead_costs,
      }
    }
    case FIELD_UPDATE_SUCCESS: {
      const { calculated_cost_pricing } = action.payload
      return {
        ...state,
        direct_total: calculated_cost_pricing.total_direct_costs,
        overhead_total: calculated_cost_pricing.total_overhead_costs,
      }
    }
    default:
      return state
  }
}
