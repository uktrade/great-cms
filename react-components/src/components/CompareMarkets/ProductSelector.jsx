import React from 'react'
import PropTypes from 'prop-types'
import { useSelector } from 'react-redux'
import { getProducts, getActiveProduct } from '@src/reducers'
import { Select } from '@src/components/Form/Select'

function ProductSelector({ setActiveProduct }) {
  const products = useSelector((state) => getProducts(state))
  const activeProduct = useSelector((state) => getActiveProduct(state))

  const setProduct = (choice) => {
    const commodityCode = Object.values(choice)[0]
    setActiveProduct(products.find((p) => p.commodity_code === commodityCode))
  }
  return (
    <>
      <Select
        label=""
        id="product-selector"
        update={setProduct}
        name="product-selector"
        options={(products || []).map((product) => {
          return {
            label: product.commodity_name,
            value: product.commodity_code,
          }
        })}
        hideLabel
        selected={activeProduct && activeProduct.commodityCode}
      />
    </>
  )
}

ProductSelector.propTypes = {
  setActiveProduct: PropTypes.func.isRequired,
}

export default ProductSelector
