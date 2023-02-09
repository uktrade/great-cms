import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'
import { Confirmation } from '@src/components/ConfirmModal/Confirmation'
import ProductFinderModal from './ProductFinderModal'
import BasketViewer from './BasketView'


function ProductFinderButton() {
  const [modalIsOpen, setIsOpen] = useState(false)
  const {products, loadProducts, productsLoaded, removeProduct} = useUserProducts(
    false, 'Personalisation bar'
  )

  const sortMap = sortMapBy(products || [], 'commodity_name')
  const [deleteConfirm, setDeleteConfirm] = useState()

  const deleteProduct = (index) => {
    removeProduct(products[index])
    setDeleteConfirm(null)
  }

  return (
    <>
      <BasketViewer label="My products" onOpen={loadProducts}>

        <ul>
          {sortMap.length === 0 && productsLoaded ? <li>My products is empty</li>: null}
          {sortMap.map((mapIndex) => {
            const product = products[mapIndex]
            return (
              <li
                key={`product-${mapIndex}`}
              >
                <span>{ReactHtmlParser(product.commodity_name)}</span>
                <button
                  type="button"
                  className="remove-product"
                  onClick={() => setDeleteConfirm({index:mapIndex})}
                >
                  <i className="fas fa-trash" />
                  <span className="visually-hidden">
                    Remove product {ReactHtmlParser(product.commodity_name)}
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
        <button
          type="button"
          className="button button--primary button--icon m-t-xs button--full-width hidden"
          onClick={() => setIsOpen(true)}
        >
          <i className="fas fa-plus" />
          Add product
      </button>
      </BasketViewer>
      {deleteConfirm && <Confirmation
        title={`Are you sure you want to remove ${products[deleteConfirm?.index].commodity_name}?`}
        yesLabel="Remove"
        yesIcon="fa-trash-alt"
        onYes={() => deleteProduct(deleteConfirm.index)}
        onNo={() => setDeleteConfirm(null)}
      />}
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
