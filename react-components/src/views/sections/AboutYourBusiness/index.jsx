import React from 'react'
import ReactDOM from 'react-dom'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const aboutYourBusinessForm = ({ element, ...params }) => {
  ReactDOM.render(<FormWithInputWithExample {...params} />, element)
}
