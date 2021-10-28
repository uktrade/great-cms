import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import ReactModal from 'react-modal'

import ProductSelector from './ProductSelector'

const valueChange = jest.fn()

const product1 = { commodity_code: '123456', commodity_name: 'product1' }
const product2 = { commodity_code: '123457', commodity_name: 'product2' }
const product3 = { commodity_code: '666666', commodity_name: 'product3' }

const userProducts = [product3, product1, product2]

const setup = () => {
  Services.setInitialState({
    userSettings: {
      UserProducts: userProducts,
      ActiveProduct: {},
    },
  })
  ReactModal.setAppElement(document.body)
  const component = render(
    <Provider store={Services.store}>
      <ProductSelector valueChange={valueChange}/>
    </Provider>
  )
  return {
    ...component,
  }
}

describe('Wizard product selector', () => {
  it('Renders product selector', () => {
    const { getByText } = setup()
    const product2Radio = getByText('product2')
    expect(product2Radio).toBeTruthy()
    fireEvent.click(product2Radio)
    expect(valueChange).toHaveBeenCalled()
    expect(valueChange).toHaveBeenCalledWith(product2)
  })
  it('Opens product finder', () => {
    const { getByText } = setup()
    const somethingElse = getByText('Something else')
    expect(somethingElse).toBeTruthy()
    fireEvent.click(somethingElse)
    const addButton = getByText('Choose a product')
    expect(addButton).toBeTruthy()
    fireEvent.click(addButton)
    expect(document.body.querySelector('.ReactModalPortal .product-finder')).toBeTruthy()

  })
})
