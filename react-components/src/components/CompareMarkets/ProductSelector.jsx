import React from 'react'
import { useUserProducts, useActiveProduct } from '@src/components/hooks/useUserData'
import { Select } from '@src/components/Form/Select'

function ProductSelector() {
  const [products] = useUserProducts()
  const [activeProduct, setActiveProduct] = useActiveProduct()

  const setProduct = (choice) => {
    const commodityCode = Object.values(choice)[0]
    setActiveProduct(products.find((p) => p.commodity_code === commodityCode))
  }
  if(activeProduct && products) {
    if(!products.find((p) => p.commodity_code === activeProduct.commodity_code && p.commodity_name === activeProduct.commodity_name) )
      setActiveProduct(products[0])
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
        selected={activeProduct && activeProduct.commodity_code}
      />
    </>
  )
}

export default ProductSelector
