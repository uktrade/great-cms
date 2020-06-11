import React from 'react'
import ReactDOM from 'react-dom'

import { BrandAndProductForm } from './BrandAndProduct'


class BusinessRationale extends BrandAndProductForm {

  formatData(data) {
    return data
  }

}

function createBusinessRationale({ element, ...params }) {
  ReactDOM.render(<BusinessRationale {...params} />, element)
}

export { BusinessRationale, createBusinessRationale }
