import React from 'react'
import ReactDOM from 'react-dom'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'
import { DataSnapShot } from '@src/components/DataSnapShot'

export const createTargetMarketResearchForm = ({ element, ...params }) => {
  ReactDOM.render(<FormWithInputWithExample {...params} />, element)
}

export const createDataSnapShot = ({ element, ...params }) => {
  ReactDOM.render(<DataSnapShot {...params} />, element)
}
