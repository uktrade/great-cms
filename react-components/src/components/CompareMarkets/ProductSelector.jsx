import React from 'react'
import {
  useUserProducts,
  useActiveProduct,
} from '@src/components/hooks/useUserData'
import { Select } from '@src/components/Form/Select'

function ProductSelector() {
  const [products] = useUserProducts()
  const [activeProduct, setActiveProduct] = useActiveProduct()

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

  return (
    <>
      <Select
        label=""
        id="product-selector"
        update={setProduct}
        name="product-selector"
        options={options}
        hideLabel
        selected={selected}
      />
    </>
  )
}

export default ProductSelector
