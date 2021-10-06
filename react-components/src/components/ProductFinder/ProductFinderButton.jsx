import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'

import BasketViewer from './BasketView'

function ProductFinderButton() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(true)
  const [selectedProductMapIndex, setSelectedProductMapIndex] = useState(null)
  const [selectedProductName, setSelectedProductName] = useState(null)
  const {products, setProducts, loadProducts} = useUserProducts(
    false
  )

  const sortMap = sortMapBy(products || [],'commodity_name')

  const deleteProduct = (index) => {
    const reduced = [...products]
    reduced.splice(index, 1)
    setProducts(reduced)
    setSelectedProductMapIndex(null)
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
              className="button button--primary button--full-width"
              onClick={() => {
                deleteProduct(selectedProductMapIndex)
              }}
            >
              Remove
            </button>
            <button
              type="button"
              className="button button--secondary button--full-width"
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
                    setSelectedProductMapIndex(mapIndex)
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
                  <div className="body-s">HS code {product.commodity_code}</div>
                </div>
              </li>
            )
          })}
        </ul>}
      </BasketViewer>
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
