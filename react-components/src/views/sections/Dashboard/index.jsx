import ReactDOM from 'react-dom'
import React from 'react'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import { getEpProduct } from '@src/reducers'

import { Dashboard } from '@src/components/Dashboard'
import DeleteButton from '@src/components/Dashboard/DeleteButton'
import CommodityCodeDetails from '@src/components/Dashboard/CommodityCodeDetails'

export const createDashboard = ({ element, ...params }) => {
  ReactDOM.render(<Dashboard {...params} />, element)
  const deleteButton = document.getElementById('export-plan-delete')
  if (deleteButton)
    ReactDOM.render(
      <Provider store={Services.store}>
        <DeleteButton />
      </Provider>,
      deleteButton
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
