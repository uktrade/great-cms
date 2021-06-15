import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import { getProducts } from '@src/reducers'
import { connect, Provider } from 'react-redux'
import Services from '@src/Services'

import ProductFinderModal from './ProductFinderModal'


function ProductFinderButton(props) {
  const { selectedProduct } = props
  const [modalIsOpen, setIsOpen] = useState(false)

  const openModal = () => {
    setIsOpen(true)
  }
  const buttonClass = `tag ${!selectedProduct ? 'tag--tertiary' : ''} tag--icon`
  const hasProduct = selectedProduct && ReactHtmlParser(selectedProduct.commodity_name)
  const triggerButton = (
    <button type="button"
      className={buttonClass}
      onClick={openModal}
    >
      {hasProduct || 'add product'}
      <span class="visually-hidden">{hasProduct ? 'Edit' : 'Add'} product</span>
      <i className={`fa ${selectedProduct ? 'fa-edit' : 'fa-plus'}`} aria-hidden="true" />
    </button>
  )

  return (
    <span>
      {triggerButton}
      <ProductFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        selectedProduct={selectedProduct}
      />
    </span>
  )
}

const mapStateToProps = (state) => {
  return {
    selectedProduct: getProducts(state),
  }
}

const ConnectedProductFinderButton = connect(mapStateToProps)(
  ProductFinderButton
)

ProductFinderButton.propTypes = {
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }),
}

ProductFinderButton.defaultProps = {
  selectedProduct: null,
}

export default function createProductFinder({ ...params }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedProductFinderButton />
    </Provider>,
    params.element
  )
}
