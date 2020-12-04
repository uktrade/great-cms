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
  overhead_total: '0.00'
}

export default (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_FIELD:
      return { ...state, ...action.payload}
    default:
      return state
  }
}
