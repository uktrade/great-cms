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
  freight_logistics: '',
  agent_distributor_fees: '',
  marketing: '',
  insurance: '',
  other_overhead_costs: '',
  direct_total: '0.00',
  overhead_total: '0.00',
  final_cost_per_unit: '',
  average_price_per_unit: '',
  net_price: '',
  local_tax_charges: '',
  duty_per_unit: '',
  gross_price_per_unit: '0',
  potential_total_profit: '0',
  gross_price_per_unit_invoicing: '',
  gross_price_per_unit_currency: '',
  profit_per_unit: '0',
  price_per_unit: '',
  export_quantity: '',
  export_units: '',
  export_end: '',
  export_end_year: '',
  estimated_costs_per_unit: '',
  units: [],
  currencies: [],
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
        total_cost_and_price,
        units,
        currencies,
      } = action.payload

      return {
        ...state,
        ...direct_costs,
        ...overhead_costs,
        units,
        currencies,
        direct_total: calculated_cost_pricing.total_direct_costs,
        overhead_total: calculated_cost_pricing.total_overhead_costs,
        profit_per_unit: calculated_cost_pricing.profit_per_unit,
        potential_total_profit: calculated_cost_pricing.potential_total_profit,
        gross_price_per_unit: calculated_cost_pricing.gross_price_per_unit,
        estimated_costs_per_unit: calculated_cost_pricing.estimated_costs_per_unit,
        final_cost_per_unit: total_cost_and_price.final_cost_per_unit,
        average_price_per_unit: total_cost_and_price.average_price_per_unit,
        net_price: total_cost_and_price.net_price,
        local_tax_charges: total_cost_and_price.local_tax_charges,
        duty_per_unit: total_cost_and_price.duty_per_unit,
        export_quantity: total_cost_and_price.export_quantity.value,
        export_units: total_cost_and_price.export_quantity.unit,
        export_end: total_cost_and_price.export_end.month,
        export_end_year: total_cost_and_price.export_end.year,
        gross_price_per_unit_invoicing: total_cost_and_price.gross_price_per_unit_invoicing_currency.value,
        gross_price_per_unit_currency: total_cost_and_price.gross_price_per_unit_invoicing_currency.unit,
      }
    }
    case FIELD_UPDATE_SUCCESS: {
      const { calculated_cost_pricing } = action.payload
      return {
        ...state,
        direct_total: calculated_cost_pricing.total_direct_costs,
        overhead_total: calculated_cost_pricing.total_overhead_costs,
        profit_per_unit: calculated_cost_pricing.profit_per_unit,
        potential_total_profit: calculated_cost_pricing.potential_total_profit,
        gross_price_per_unit: calculated_cost_pricing.gross_price_per_unit,
        estimated_costs_per_unit: calculated_cost_pricing.estimated_costs_per_unit,
      }
    }
    default:
      return state
  }
}
