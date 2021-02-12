import React from 'react'
import ReactDOM from 'react-dom'

import { BusinessRisks } from '@src/components/BusinessRisk/BusinessRisks/BusinessRisks'

export const businessRisks = ({ element, ...params }) => {
  ReactDOM.render(<BusinessRisks {...params} />, element)
}
