import React from 'react'
import ReactDOM from 'react-dom'

import { Login } from '@src/components/Login'

export const createLogin = ({ element, ...params }) => {
  ReactDOM.render(<Login {...params} />, element)
}
