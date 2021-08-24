import React, { useState } from 'react'

import {
  useUserProducts,
  useActiveProduct,
} from '@src/components/hooks/useUserData'

import { Select } from '@src/components/Form/Select'
import { sortBy } from '@src/Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'

function ProductSelector() {
  const [selectedProducts] = useUserProducts()
  const [activeProduct, setActiveProduct] = useActiveProduct()
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)

  const products = sortBy(selectedProducts || [],'commodity_name')

  const setProduct = (choice) => {
    const index = Object.values(choice)[0]
    setActiveProduct(products[index])
  }

  // Check that the active product is in our product list
  // If not, set it to the first
  if (activeProduct && products) {
    if (
      !products.find(
        (p) =>
          p.commodity_code === activeProduct.commodity_code &&
          p.commodity_name === activeProduct.commodity_name
      )
    ) {
      setActiveProduct(products[0])
    }
  }

  const options = (products || []).map((product, index) => {
    return {
      label: product.commodity_name,
      value: `${index}`,
    }
  })

  const selected = `${(products || []).findIndex(
    (p) =>
      activeProduct &&
      activeProduct.commodity_code === p.commodity_code &&
      activeProduct.commodity_name === p.commodity_name
  )}`

  const hasProducts =  !!products.length

  return (
    <>
      <div className="body-l-b">{hasProducts ? 'Select your product' : 'You haven\'t selected any products'}</div>
      { hasProducts ?
      <div className="f-l m-r-s p-b-xs w-full-mobile" style={{minWidth:'250px'}}>

      <Select
        label=""
        id="product-selector"
        update={setProduct}
        name="product-selector"
        options={options}
        hideLabel
        selected={selected}
        className=""
      />
      </div> : ''}
      <button
        type="button"
        className="f-l m-t-xxs button button--tertiary button--icon button--small"
        onClick={() => setProductModalIsOpen(true)}
      >
        <i className="fa fa-plus-circle" />
        { hasProducts ? 'Add another product' : 'Add a product' }
      </button>
      <ProductFinderModal
        modalIsOpen={productModalIsOpen}
        setIsOpen={setProductModalIsOpen}
      />
    </>
  )
}
export default ProductSelector
