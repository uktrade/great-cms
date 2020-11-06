import React from 'react'
import ReactDOM from 'react-dom'

import { RouteToMarket } from '@src/components/RouteToMarket'
import { SpendingAndResources } from '@src/components/SpendingAndResources'
import { TargetAgeGroupInsights } from '@src/components/TargetAgeGroupInsights'

export const createRouteToMarket = ({ element, ...params }) => {
  ReactDOM.render(<RouteToMarket {...params} />, element)
}

export const createSpendingAndResources = ({ element, ...params }) => {
  ReactDOM.render(<SpendingAndResources {...params} />, element)
}

export const createTargetAgeGroupInsights = ({ element, ...params }) => {
  ReactDOM.render(<TargetAgeGroupInsights {...params} />, element)
}
