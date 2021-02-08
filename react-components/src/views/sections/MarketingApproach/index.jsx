import React from 'react'
import ReactDOM from 'react-dom'

import { RouteToMarket } from '@src/components/RouteToMarket'
import { TargetAgeGroupInsights } from '@src/components/TargetAgeGroupInsights'
import { FormElements } from '@src/components/FormElements'

export const createRouteToMarket = ({ element, ...params }) => {
  ReactDOM.render(<RouteToMarket {...params} />, element)
}

export const createSpendingAndResources = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}

export const createTargetAgeGroupInsights = ({ element, ...params }) => {
  ReactDOM.render(<TargetAgeGroupInsights {...params} />, element)
}
