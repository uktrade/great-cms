import ReactDOM from 'react-dom'
import React from 'react'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import { getEpProduct } from '@src/reducers'

import { Dashboard } from '@src/components/Dashboard'
import ActionBar from '@src/components/Dashboard/ActionBar'
import CommodityCodeDetails from '@src/components/Dashboard/CommodityCodeDetails'

export const createDashboard = ({ element, ...params }) => {
  ReactDOM.render(<Dashboard {...params} />, element)
  const actionsContainer = document.getElementById('export-plan-actions')
  if (actionsContainer)
    ReactDOM.render(
      <Provider store={Services.store}>
        <ActionBar {...params}/>
      </Provider>,
      actionsContainer
    )
  const commodityCodeSection = document.getElementById('section-commodity-code')
  if (commodityCodeSection) {
    const epProduct = getEpProduct(Services.store.getState())
    ReactDOM.render(
        <CommodityCodeDetails product={epProduct}/>,
      commodityCodeSection
    )
  }
}
