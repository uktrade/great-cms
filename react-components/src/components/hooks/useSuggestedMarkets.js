import { useState, useEffect } from 'react'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'

// Returns the list of suggested markets based on the list of products provided.
// If no product list provided - use basket instead

export const useSuggestedMarkets = (products) => {
  const {
    products: userProducts,
    loadProducts: loadUserProducts,
  } = useUserProducts(false)
  const [suggestedCountries, setSuggestedCountries] = useState({})

  const getHS2Code = () => {
    if (!products && !userProducts.length) {
      loadUserProducts()
    }
    const productList = products || userProducts || []
    const product = productList[productList.length - 1] || {}
    const hs2 = (product.commodity_code || '').substr(0, 2)
    const allSame =
      productList.length > 1 &&
      !productList.find(
        (scanProduct) => (scanProduct.commodity_code || '').substr(0, 2) !== hs2
      )
    return {
      hs2,
      product: product.commodity_name,
      allSame,
    }
  }

  const loadSuggestedCountries = () => {
    const activeHs2 = getHS2Code(products)
    if (activeHs2) {
      if ((suggestedCountries || {}).hs2 !== activeHs2.hs2) {
        Services.getSuggestedCountries(activeHs2.hs2).then((result) => {
          setSuggestedCountries({
            hs2: activeHs2.hs2,
            details: activeHs2,
            suggestions: result,
          })
        })
      } else {
        setSuggestedCountries({
          ...suggestedCountries,
          details: activeHs2,
        })
      }
    }
  }

  useEffect(() => {
    if (!products && userProducts.length) {
      loadSuggestedCountries()
    }
  }, [userProducts])

  return { suggestedCountries, loadSuggestedCountries }
}
