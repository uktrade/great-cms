import ReactDOM from 'react-dom'
import React from 'react'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import { Dashboard } from '@src/components/Dashboard'
import DeleteButton from '@src/components/Dashboard/DeleteButton'

export const createDashboard = ({ element, ...params }) => {
  ReactDOM.render(<Dashboard {...params} />, element)
  const deleteButton = document.body.querySelector('.export-plan-delete')
  if (deleteButton)
    ReactDOM.render(
      <Provider store={Services.store}>
        <DeleteButton />
      </Provider>,
      deleteButton
    )
}
