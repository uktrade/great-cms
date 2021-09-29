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
  const [isDropdownOpen, setIsDropdownOpen] = useState(true)
  const [selectedProductID, setSelectedProductID] = useState(null)
  const [selectedProductName, setSelectedProductName] = useState(null)
  const {products, setProducts, loadProducts} = useUserProducts(
    false
  )

  const sortMap = sortMapBy(products || [],'commodity_name')

  const deleteProduct = (index) => {
    const reduced = [...products]
    reduced.splice(index, 1)
    setProducts(reduced)
    setSelectedProductID(null)
    setSelectedProductName(null)
    setIsDropdownOpen(false)
  }

  return (
    <>
      <BasketViewer dropdownOpen={isDropdownOpen} disabled={!products.length} label="My products" onOpen={loadProducts}>


        {selectedProductName && <div className="remove-confirmation">
          <div className="item-remove-title h-xs">
            Are you sure you want to remove {selectedProductName} ?
          </div>
          <div className="remove-buttons">
            <button
              type="button"
              className="button button--primary"
              onClick={() => {
                deleteProduct(selectedProductID)
              }}
            >
              Remove
            </button>
            <button
              type="button"
              className="button button--secondary"
              onClick={() => {
                setSelectedProductName(null)
              }}
            >
              Cancel
            </button>
          </div>
        </div>}


        {!selectedProductName && <ul className="list m-v-0 body-l-b">
          {sortMap.map((mapIndex) => {
            const product = products[mapIndex]

            return (
              <li
                className="p-v-xxs"
                key={`product-${mapIndex}`}
              >
                <button
                  type="button"
                  className="button button--small button--only-icon button--tertiary"
                  onClick={() => {
                    setSelectedProductID(mapIndex)
                    setSelectedProductName(product.commodity_name)
                  }}
                >
                  <i className="fas fa-times" />
                  <span className="visually-hidden">
                    Remove product {ReactHtmlParser(product.commodity_name)}
                  </span>
                </button>
                <div>
                  <div>{ReactHtmlParser(product.commodity_name)}</div>
                  <div className="product-subtitle">HS code {product.commodity_code}</div>
                </div>
              </li>
            )
          })}
        </ul>}
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
