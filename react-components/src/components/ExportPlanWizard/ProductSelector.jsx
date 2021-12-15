import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserProducts } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import { sortBy } from '@src/Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'

function ProductSelector({ valueChange, selected }) {
  const { products, productsLoaded } = useUserProducts()
  const [modalIsOpen, setModalIsOpen] = useState(false)
  const [addButtonShowing, setAddButtonShowing] = useState(false)

  let selectedKey

  const isProductSelected = (product) =>
    selected &&
    selected.commodity_code === product.commodity_code &&
    selected.commodity_name === product.commodity_name

  // It's possible (during an update) that the selected product is not in the list of user products
  // In this case, we need to add it to the list
  if (selected && selected.commodity_code) {
    if (!products.filter(isProductSelected).length) {
      products.push(selected)
    }
  }
  const sortedProducts = sortBy(products || [], 'commodity_name')
  const options = sortedProducts.map((product, index) => {
    if (isProductSelected(product)) {
      selectedKey = `${index}`
    }
    return {
      label: (
        <div>{product.commodity_name}</div>
      ),
      value: `${index}`,
    }
  })
  const somethingElse = {
    label: 'Something else',
    value: '+',
  }
  const onValueChange = (index) => {
    setAddButtonShowing(index === '+')
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

      {((productsLoaded && !hasProducts) || addButtonShowing) && (
        <div className={`${addButtonShowing ? 'g-panel' : ''} m-f-xxs`}>
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
