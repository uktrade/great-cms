import React from 'react'
import ReactDOM from 'react-dom'

import { AdaptToTargetMarketForm } from '@src/views/sections/AdaptationForYourTargetMarket/adaptToTargetMarketForm'

export const adaptToTargetMarketForm = ({ element, ...params }) => {
  ReactDOM.render(<AdaptToTargetMarketForm {...params} />, element)
}
