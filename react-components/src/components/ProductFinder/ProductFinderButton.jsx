import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Confirmation from './MessageConfirmation'
import ProductFinderModal from './ProductFinderModal'


function ProductFinderButton(props) {
  const { product } = props;
  const [modalIsOpen, setIsOpen] = useState(false)
  const [productConfirmationRequired, setProductConfirmationRequired] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(product)

  const openModal = () => {
    setProductConfirmationRequired(!!selectedProduct)
    setIsOpen(!selectedProduct)
  }

  const closeConfirmation = () => {
    setProductConfirmationRequired(false)
    setIsOpen(true)
  }

  let triggerButton = (
    <button type="button" 
      className="button button--primary button--icon m-v-xl"
      onClick={openModal}>
        <i className="fa fa-plus-square"/>
      Select product
    </button>)
  const buttonClass = `tag ${!selectedProduct ? 'tag--tertiary' : ''} tag--icon`
  if (selectedProduct !== null) {
    triggerButton = (
      <button type="button" className={buttonClass} onClick={openModal}>
        {selectedProduct || 'add product'}
        <i className={`fa ${selectedProduct ? 'fa-edit' : 'fa-plus'}`}/>
      </button>
    )
  }

  return (
    <span>
      {triggerButton}
      <ProductFinderModal 
        modalIsOpen={ modalIsOpen }
        setIsOpen={ setIsOpen }
        setSelectedProduct={ setSelectedProduct }
      />
      <Confirmation
          buttonClass={buttonClass}
          productConfirmation={productConfirmationRequired}
          handleButtonClick={closeConfirmation}
          messageTitle="Changing product?"
          messageBody="if you've created an export plan, make sure you update it to reflect your new product. you can change product at any time."
          messageButtonText="Got it"
      />
    </span>
  )
}

ProductFinderButton.propTypes = {
  product: PropTypes.string,
}

ProductFinderButton.defaultProps = {
  product: '',
}

export default function createProductFinder({ ...params }) {
  const product = params.element.getAttribute('data-text')
  ReactDOM.render(<ProductFinderButton product={product} />, params.element)
}
