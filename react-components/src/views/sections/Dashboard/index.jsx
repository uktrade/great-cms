import ReactDOM from 'react-dom'
import React from 'react'

import { Dashboard } from '@src/components/Dashboard'
import { Buttons } from './Buttons'

export const createDashboard = ({ element, ...params }) => {
  debugger
  ReactDOM.render(<Dashboard {...params} />, element)
}

export const createDisabledButton = ({ element }) => {
  ReactDOM.render(<Buttons />, element)
}
