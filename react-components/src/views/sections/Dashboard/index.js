import React from 'react'
import ReactDOM from 'react-dom'

import { Dashboard } from '@src/components/Dashboard'

export const createDashboard = ({ element, ...params }) => {
  ReactDOM.render(<Dashboard {...params} />, element)
}
