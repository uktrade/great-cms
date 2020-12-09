import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'
import { DataSnapShot } from '@src/components/DataSnapShot'

export const createTargetMarketResearchForm = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}

export const createDataSnapShot = ({ element, ...params }) => {
  ReactDOM.render(<DataSnapShot {...params} />, element)
}
