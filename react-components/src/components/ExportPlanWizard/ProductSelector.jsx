import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserProducts } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'

function ProductSelector({ valueChange, selected }) {
  const [products] = useUserProducts()
  const [modalIsOpen, setModalIsOpen] = useState(false)

  let selectedIndex

  const options = (products || []).map((product, index) => {
    if (
      selected &&
      selected.commodity_code === product.commodity_code &&
      selected.commodity_name === product.commodity_name
    ) {
      selectedIndex = `${index}`
    }
    return {
      label: product.commodity_name,
      value: `${index}`,
    }
  })

  return (
    <>
      <div className="clearfix">
        <RadioButtons
          name="selected-product"
          choices={options}
          valueChange={(index) => valueChange(products[index])}
          initialSelection={selectedIndex}
        />
      </div>
      <button
        type="button"
        className="f-l m-t-xxs button button--tertiary button--icon"
        onClick={() => setModalIsOpen(true)}
      >
        <i className="fa fa-plus-square" />
        Add a product
      </button>
      <ProductFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setModalIsOpen}
      />
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
