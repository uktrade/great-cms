import ReactDOM from 'react-dom'
import React from 'react'

import { CostsAndPricing } from '@src/components/CostsAndPricing'

export const createCostsAndPricing = ({ element, ...params }) => {
  ReactDOM.render(<CostsAndPricing {...params} />, element)
}
