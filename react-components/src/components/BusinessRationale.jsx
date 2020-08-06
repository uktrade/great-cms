import React from 'react'
import ReactDOM from 'react-dom'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

class BusinessRationale extends FormWithInputWithExample {

  formatData(data) {
    return data
  }

}

function createBusinessRationale({ element, ...params }) {
  ReactDOM.render(<BusinessRationale {...params} />, element)
}

export { BusinessRationale, createBusinessRationale }
