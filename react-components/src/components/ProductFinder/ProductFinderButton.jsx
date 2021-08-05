import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import { getProducts } from '@src/reducers'
import { Provider, useSelector } from 'react-redux'
import Services from '@src/Services'
import actions from '@src/actions'

import ProductFinderModal from './ProductFinderModal'
import BasketViewer from './BasketView'

const userProductsKey = 'UserProducts'

function ProductFinderButton() {
  const [modalIsOpen, setIsOpen] = useState(false)
  const selectedProducts = useSelector((state) => getProducts(state))

  const loadProducts = () => {
    // Load the product list into redux.  We'll be needing it later
    if (!selectedProducts)
      Services.getUserData(userProductsKey).then((result) => {
        Services.store.dispatch(actions.setProducts(result[userProductsKey]))
      })
  }

  const openModal = () => {
    setIsOpen(true)
  }

  const onOpenView = () => {
    loadProducts()
  }

  const deleteProduct = (index) => {
    const reduced = [...selectedProducts]
    reduced.splice(index,1)
    Services.store.dispatch(actions.setProducts(reduced))
  }

  return (
    <>
      <BasketViewer label="My products" onOpen={onOpenView}>
        <ul className="list m-v-0">
          {(selectedProducts || []).map((product, index) => (
            <li key={`product-${index}`}>
              {ReactHtmlParser(product.commodity_name)} <button className="f-r" onClick={() => deleteProduct(index)}><i className="fas fa-trash-alt"/><span className="visually-hidden">Remove product {ReactHtmlParser(product.commodity_name)}</span></button>
            </li>
          ))}
        </ul>
        <button className="button button--primary m-t-xs" onClick={openModal}>
          Add product
        </button>
      </BasketViewer>
      <ProductFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        selectedProducts={selectedProducts}
      />
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
