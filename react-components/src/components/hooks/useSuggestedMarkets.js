import { useState, useEffect } from 'react'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'

// Returns the list of suggested markets based on the list of products provided.
// If no product list provided - use basket instead

export const useSuggestedMarkets = (products) => {
  const [userProducts, setUserProducts, loadUserProducts] = useUserProducts(
    false
  )
  const [suggestedCountries, setSuggestedCountries] = useState({})

  const getHS2Code = () => {
    if (!products && !userProducts.length) {
      loadUserProducts()
    }
    const productList = products || userProducts || []
    const uniqueList = productList.reduce((out, product) => {
      const prodHs2 = (product.commodity_code || '').substr(0, 2)
      out[prodHs2] = out[prodHs2] || product.commodity_name
      return {...out}
    }, {})
    const hs2 = Object.keys(uniqueList)[0]
    return {
      hs2,
      product: uniqueList[hs2],
      allSame: productList.length > 1 && Object.keys(uniqueList).length === 1,
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
