import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'

export const financeTotalExportCost = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}

export const financeHowMuchFunding = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}

export const financeFundingCreditOptions = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}
