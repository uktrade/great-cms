import {
  UPDATE_FIELD,
  FIELD_UPDATE_SUCCESS,
  INIT_COST_PRICING,
} from '@src/actions/costsAndPricing'
import { getLabel } from '@src/Helpers'

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
  units_to_export: '',
  export_units: '',
  time_frame: '',
  export_time_frame: '',
  timeframe: [],
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
        timeframe,
        units,
        currencies,
      } = action.payload

      return {
        ...state,
        ...direct_costs,
        ...overhead_costs,
        timeframe,
        units,
        currencies,
        direct_total: calculated_cost_pricing.total_direct_costs,
        overhead_total: calculated_cost_pricing.total_overhead_costs,
        profit_per_unit: calculated_cost_pricing.profit_per_unit,
        potential_total_profit: calculated_cost_pricing.potential_total_profit,
        gross_price_per_unit: calculated_cost_pricing.gross_price_per_unit,
        final_cost_per_unit: total_cost_and_price.final_cost_per_unit,
        average_price_per_unit: total_cost_and_price.average_price_per_unit,
        net_price: total_cost_and_price.net_price,
        local_tax_charges: total_cost_and_price.local_tax_charges,
        duty_per_unit: total_cost_and_price.duty_per_unit,
        units_to_export:
          total_cost_and_price.units_to_export_first_period.value,
        export_units: getLabel(
          units,
          total_cost_and_price.units_to_export_first_period.unit
        ),
        time_frame: total_cost_and_price.units_to_export_second_period.value,
        export_time_frame: getLabel(
          timeframe,
          total_cost_and_price.units_to_export_second_period.unit
        ),
        gross_price_per_unit_invoicing:
          total_cost_and_price.gross_price_per_unit_invoicing_currency.value,
        gross_price_per_unit_currency: getLabel(
          currencies,
          total_cost_and_price.gross_price_per_unit_invoicing_currency.unit
        ),
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
      }
    }
    default:
      return state
  }
}
