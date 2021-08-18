import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'

import ProductFinderModal from './ProductFinderModal'
import BasketViewer from './BasketView'

function ProductFinderButton() {
  const [modalIsOpen, setIsOpen] = useState(false)
  const [selectedProducts, setSelectedProducts, loadProducts] = useUserProducts(
    false
  )

  const sortMap = sortMapBy(selectedProducts || [])

  const deleteProduct = (index) => {
    const reduced = [...selectedProducts]
    reduced.splice(index, 1)
    setSelectedProducts(reduced)
  }

  return (
    <>
      <BasketViewer label="My products" onOpen={loadProducts}>
        <ul className="list m-v-0 body-l-b">
          {sortMap.map((mapIndex) => {
            const product = selectedProducts[mapIndex]
            return (
              <li
                className="p-v-xxs"
                key={`product-${mapIndex}`}
              >
                <button
                  type="button"
                  className="button button--small button--only-icon button--tertiary"
                  onClick={() => deleteProduct(mapIndex)}
                >
                  <i className="fas fa-trash-alt" />
                  <span className="visually-hidden">
                    Remove product {ReactHtmlParser(product.commodity_name)}
                  </span>
                </button>
                {ReactHtmlParser(product.commodity_name)}
              </li>
            )
          })}
        </ul>
        <button
          type="button"
          className="button button--primary button--icon m-t-xs button--full-width"
          onClick={() => setIsOpen(true)}
        >
          <i className="fas fa-plus" />
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
