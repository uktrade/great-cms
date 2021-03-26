import React from 'react'
import ReactDOM from 'react-dom'

import { Provider } from 'react-redux'
import Services from '@src/Services'
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
	ReactDOM.render(
		<Provider store={Services.store}>
			<TargetAgeGroupInsights {...params} />
		</Provider>,
		element
	)
}
