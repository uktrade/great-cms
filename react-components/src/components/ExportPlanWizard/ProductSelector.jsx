import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserProducts } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import { sortBy } from '@src/Helpers'

function ProductSelector({ valueChange, selected }) {
  const [products] = useUserProducts()
  const [modalIsOpen, setModalIsOpen] = useState(false)
  const [addButtonShowing, setAddButtonShowing] = useState(false)

  const sortedProducts = sortBy(products || [], 'commodity_name')
  let selectedKey

  const options = sortedProducts.map((product, index) => {
    if (
      selected &&
      selected.commodity_code === product.commodity_code &&
      selected.commodity_name === product.commodity_name
    ) {
      selectedKey = `${index}`
    }
    return {
      label: (
        <>
          <div>{product.commodity_name}</div>
          <div className="body-m">HS6 code: {product.commodity_code}</div>
        </>
      ),
      value: `${index}`,
    }
  })
  const somethingElse = {
    label: 'Something else',
    value: '+',
  }
  const onValueChange = (index) => {
    setAddButtonShowing(index == '+')
    valueChange(sortedProducts[index])
  }
  const onProductAdded = (product) => {
    setAddButtonShowing(false)
    valueChange(product)
  }

  // If the add button is showing, 'something else' option must be selected
  selectedKey = selectedKey || (addButtonShowing ? '+' : '')
  const hasProducts = products && products.length

  return (
    <>
      {hasProducts ? (
        <div className="clearfix">
          <RadioButtons
            name="selected-product"
            choices={[...options, somethingElse]}
            valueChange={onValueChange}
            initialSelection={selectedKey}
          />
        </div>
      ) : null}

      {(!hasProducts || addButtonShowing) && (
        <div className="g-panel m-f-xxs">
          <button
            type="button"
            className="m-t-xxs button button--primary"
            onClick={() => setModalIsOpen(true)}
          >
            <i className="fa fa-plus m-r-xxs" />
            Choose a product
          </button>
        </div>
      )}
      {modalIsOpen && (
        <ProductFinderModal
          modalIsOpen={modalIsOpen}
          setIsOpen={setModalIsOpen}
          onAddProduct={onProductAdded}
        />
      )}
    </>
  )
}

export default ProductSelector

ProductSelector.propTypes = {
  valueChange: PropTypes.func.isRequired,
  selected: PropTypes.shape({
    commodity_code: PropTypes.string,
    commodity_name: PropTypes.string,
  }),
}

ProductSelector.defaultProps = {
  selected: null,
}
