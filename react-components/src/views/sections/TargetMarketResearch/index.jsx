import React from 'react'
import ReactDOM from 'react-dom'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { FormElements } from '@src/components/FormElements'
import { DataSnapShot } from '@src/components/DataSnapShot'

export const createTargetMarketResearchForm = ({ element, ...params }) => {
  ReactDOM.render(
    <Provider store={Services.store}>
      <FormElements {...params} />
    </Provider>,
    element
  )
}

export const createDataSnapShot = ({ element, ...params }) => {
  ReactDOM.render(
    <Provider store={Services.store}>
      <DataSnapShot {...params} />
    </Provider>,
    element
  )
}
