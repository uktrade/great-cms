import ReactDOM from 'react-dom'
import React from 'react'

import { GettingPaid } from '@src/components/GettingPaid/GettingPaid'

export const createGettingPaid = ({ element, ...params }) => {
  ReactDOM.render(<GettingPaid {...params} />, element)
}
