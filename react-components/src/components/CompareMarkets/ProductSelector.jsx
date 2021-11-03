import React, { useState } from 'react'

import {
  useUserProducts,
  useActiveProduct,
} from '@src/components/hooks/useUserData'

import { Select } from '@src/components/Form/Select'
import { sortBy, deepEqual, analytics } from '@src/Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'

function ProductSelector() {
  const { products: unsortedProducts } = useUserProducts()
  const [activeProduct, setActiveProduct] = useActiveProduct()
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)

  const products = sortBy(unsortedProducts || [], 'commodity_name')

  const setProduct = (choice) => {
    const index = Object.values(choice)[0]
    setActiveProduct(products[index])
    analytics({
      event: 'selectGridProduct',
      gridProductSelected:`${products[index].commodity_code}|${products[index].commodity_name}`
    })

  }

  const options = (products || []).map((product, index) => {
    return {
      label: product.commodity_name,
      value: `${index}`,
    }
  })
  let selectedIndex = (products || []).findIndex((p) =>
    deepEqual(p, activeProduct)
  )
  if(selectedIndex < 0 && products.length) {
    selectedIndex = products.length-1
    setActiveProduct(products[selectedIndex])
  }
  if(!products.length && activeProduct !== '') {
    selectedIndex = null
    setActiveProduct('')
  }

  const hasProducts = !!products.length

  return (
    <>
      <div className="body-l-b">
        {hasProducts
          ? 'Select your product'
          : "You haven't selected any products"}
      </div>
      {hasProducts ? (
        <div
          className="f-l m-r-s p-b-xs w-full-mobile"
          style={{ minWidth: '250px' }}
        >
          <Select
            label=""
            id="product-selector"
            update={setProduct}
            name="product-selector"
            options={options}
            hideLabel
            selected={`${selectedIndex}`}
            className=""
          />
        </div>
      ) : (
        ''
      )}
      <button
        type="button"
        className="f-l m-t-xxs button button--tertiary button--icon button--small"
        onClick={() => setProductModalIsOpen(true)}
      >
        <i className="fa fa-plus-circle" />
        {hasProducts ? 'Add another product' : 'Add a product'}
      </button>
      <ProductFinderModal
        modalIsOpen={productModalIsOpen}
        setIsOpen={setProductModalIsOpen}
      />
    </>
  )
}
export default ProductSelector
