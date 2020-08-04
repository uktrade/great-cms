import React from 'react'
import ReactDOM from 'react-dom'

import { RouteToMarket } from '@src/views/sections/MarketingApproach/RouteToMarket'
import { SpendingAndResources } from '@src/views/sections/MarketingApproach/SpendingAndResources'

export const createRouteToMarket = ({ element, ...params }) => {
  ReactDOM.render(<RouteToMarket {...params} />, element)
}

export const createSpendingAndResources = ({ element, ...params }) => {
  ReactDOM.render(<SpendingAndResources {...params} />, element)
}
