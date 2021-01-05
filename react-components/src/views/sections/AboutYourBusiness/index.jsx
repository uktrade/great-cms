import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'

export const aboutYourBusinessForm = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}
