import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'

import ProductFinderModal from './ProductFinderModal'
import BasketViewer from './BasketView'

function ProductFinderButton() {
  const [modalIsOpen, setIsOpen] = useState(false)
  const [selectedProducts, setSelectedProducts, loadProducts] =
    useUserProducts(false)

  const openModal = () => {
    setIsOpen(true)
  }

  const onOpenView = () => {
    loadProducts()
  }

  const deleteProduct = (index) => {
    const reduced = [...selectedProducts]
    reduced.splice(index, 1)
    setSelectedProducts(reduced)
  }

  return (
    <>
      <BasketViewer label="My products" onOpen={onOpenView}>
        <ul className="list m-v-0 body-l-b">
          {(selectedProducts || []).map((product, index) => (
            <li className="p-v-xxs" key={`product-${product.commodity_code}-${product.commodity_name}`}>
              {ReactHtmlParser(product.commodity_name)}
              <button
                type="button"
                className="f-r button button--small button--only-icon button--tertiary"
                onClick={() => deleteProduct(index)}
              >
                <i className="fas fa-trash-alt" />
                <span className="visually-hidden">
                  Remove product {ReactHtmlParser(product.commodity_name)}
                </span>
              </button>
            </li>
          ))}
        </ul>
        <button
          type="button"
          className="button button--primary button--icon m-t-xs button--full-width"
          onClick={openModal}
        >
          <i className="fas fa-plus"/>
          Add product
        </button>
      </BasketViewer>
      <ProductFinderModal modalIsOpen={modalIsOpen} setIsOpen={setIsOpen} />
    </>
  )
}

export default function createProductFinder({ ...params }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <ProductFinderButton />
    </Provider>,
    params.element
  )
}
