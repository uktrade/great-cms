import {
  UPDATE_FIELD,
  FIELD_UPDATE_SUCCESS,
} from '@src/actions/costsAndPricing'

export const initialState = {
  product_costs: '',
  labour_costs: '',
  additional_margin: '',
  product_adaption: '',
  packaging: '',
  freight: '',
  agent: '',
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
}

export default (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_FIELD:
      return { ...state, ...action.payload }
    case FIELD_UPDATE_SUCCESS:
      return { ...state }
    default:
      return state
  }
}
