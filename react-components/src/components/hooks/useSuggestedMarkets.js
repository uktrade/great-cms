import { useState, useEffect } from 'react'
import Services from '@src/Services'
import { useUserProducts } from '@src/components/hooks/useUserData'
import { get } from '@src/Helpers'

// Returns the list of suggested markets based on the list of products provided.
// If no product list provided - use basket instead

const capitalize = (str) =>
  `${str.charAt(0).toUpperCase()}${str.slice(1).toLowerCase()}`

let localState = {}

export const useSuggestedMarkets = (products) => {
  const {
    products: userProducts,
    loadProducts: loadUserProducts,
    productsLoaded: userProductsLoaded,
  } = useUserProducts(false)
  const [suggestedCountries, setSuggestedCountries] = useState(
    'suggested_countries'
  )

  const setLocalState = (newState) => {
    localState = { ...localState, ...newState }
    if (localState.details && localState.hs2Desc)
      setSuggestedCountries(localState)
  }

  const getHS2Code = () => {
    if (!products && !userProductsLoaded) {
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
      hs6: product.commodity_code,
      hs2,
      product: product.commodity_name,
      allSame,
    }
  }

  const loadSuggestedCountries = () => {
    const activeHs2 = getHS2Code(products)

    if (activeHs2) {
      if (localState.hs2 !== activeHs2.hs2) {
        setLocalState({
          hs2: activeHs2.hs2,
          details: activeHs2,
        })
        Services.getSuggestedCountries(activeHs2.hs2).then((result) => {
          setLocalState({
            suggestions: result,
          })
        })
        Services.lookupProductSchedule({ hsCode: activeHs2.hs6 }).then(
          (results) => {
            setLocalState({
              hs2Desc: capitalize(
                get(results, 'children.0.children.0.desc', '').replace(
                  /^chapter[\d\s-]*/i,
                  ''
                ) || ''
              ),
            })
          }
        )
      }
      setSuggestedCountries(localState)
    }
  }

  useEffect(() => {
    if (!products && userProducts.length) {
      loadSuggestedCountries()
    }
  }, [userProducts])

  return { suggestedCountries, loadSuggestedCountries }
}
