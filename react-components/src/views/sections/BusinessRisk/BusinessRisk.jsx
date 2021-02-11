import React from 'react'
import ReactDOM from 'react-dom'

import { Risks } from '@src/components/BusinessRisk/Risks/Risks'

export const businessRisks = ({ element, ...params }) => {
  ReactDOM.render(<Risks {...params} />, element)
}
