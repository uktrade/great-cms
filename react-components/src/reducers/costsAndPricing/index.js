import { UPDATE_FIELD } from '@src/actions/costsAndPricing'

export const initialState = {
  product: '',
  labour: '',
  additional_margin: '',
  adaptation: '',
  packaging: '',
  freight: '',
  agent: '',
  marketing: '',
  insurance: '',
  other_overhead: '',
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
  export_units: ''
}

export default (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_FIELD:
      return { ...state, ...action.payload}
    default:
      return state
  }
}
