import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'

import ProductFinderModal from './ProductFinderModal'
import BasketViewer from './BasketView'

import { Confirmation } from '@src/components/ConfirmModal/Confirmation'

function ProductFinderButton() {
  const [modalIsOpen, setIsOpen] = useState(false)
  const {products, setProducts, loadProducts} = useUserProducts(
    false
  )

  const sortMap = sortMapBy(products || [], 'commodity_name')
  const [deleteConfirm, setDeleteConfirm] = useState({
    delete: null,
    index: null,
    name: null
  })

  const confirmDelete = (name, index) => {
    setDeleteConfirm({
      delete: true,
      index: index,
      name: name
    })
  }

  const deleteProduct = (index) => {
    const reduced = [...products]
    reduced.splice(index, 1)
    setProducts(reduced)
    setDeleteConfirm({
      ...confirmDelete,
      delete: false
    })
  }

  return (
    <>
      <BasketViewer label="My products" onOpen={loadProducts}>
        {sortMap.length === 0 ? <p class="body-l-b text-center">My products is empty</p>: null}
        <ul className="list m-v-0 body-l-b">
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
                  onClick={() => confirmDelete(product.commodity_name, mapIndex)}
                >
                  <i className="fas fa-times fa-lg" />
                  <span className="visually-hidden">
                    Remove product {ReactHtmlParser(product.commodity_name)}
                  </span>
                </button>
                {ReactHtmlParser(product.commodity_name)}
              </li>
            )
          })}
        </ul>
      </BasketViewer>
      {deleteConfirm.delete && <Confirmation
        title={`Are you sure you want to remove ${deleteConfirm.name}?`}
        yesLabel="Remove"
        yesIcon="fa-trash-alt"
        onYes={() => deleteProduct(deleteConfirm.index)}
        onNo={() => setDeleteConfirm({...deleteConfirm, delete: false})}
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
