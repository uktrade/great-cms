import Services from '@src/Services'
import actions from '@src/actions'
import { isObject, isArray, deepEqual } from '@src/Helpers'
import { useSelector } from 'react-redux'

const loading = {} // flag when data are being retrieved

// User settings items. These are async and the global state will get populated once complete
// default: is set on completion of retrieval is the object does not already exist
// autoload: can be set false to stop the blob from loading automatically. In that case, call the load method to initiate loading
// duplicateComparator: If a list, check for duplicates by calling this fn(a,b). Default is full deep comparison.

export const useUserData = (
  blobName,
  defaultValue = [],
  autoload = true,
  duplicateComparator = deepEqual
) => {
  const blobValue = useSelector(
    (state) => state.userSettings && state.userSettings[blobName]
  )

  const saveBlob = (value) =>
    Services.store.dispatch(actions.setUserData(blobName, value))

  const loadBlob = () => {
    if (!blobValue && !loading[blobName]) {
      loading[blobName] = 1
      Services.getUserData(blobName).then((result) => {
        loading[blobName] = 'loaded'
        const value = isObject(result) && (result[blobName] || defaultValue)
        saveBlob(value)
      })
    }
  }
  if (autoload) {
    loadBlob()
  }

  const addToList = (item) => {
    // Where the blob is a list, this method adds the given item to the end only if it's unique
    if (blobValue && isArray(blobValue)) {
      const duplicate = blobValue.reduce((out, cItem) => {
        return out || duplicateComparator(cItem, item)
      }, false)
      if (!duplicate) {
        saveBlob([...blobValue, item])
      }
    }
  }

  const removeFromList = (item) => {
    // Where the blob is a list, this method adds the given item to the end only if it's unique
    if (blobValue && isArray(blobValue)) {
      const index = blobValue.findIndex((cItem) =>
        duplicateComparator(cItem, item)
      )
      if(index >= 0) {
        const reduced = [...blobValue]
        reduced.splice(index, 1)
        saveBlob(reduced)
      }
    }
  }

  return [
    blobValue || defaultValue,
    saveBlob,
    loadBlob,
    blobValue || (loading[blobName] === 'loaded'),
    addToList,
    removeFromList,
  ]
}

export const useActiveProduct = (autoload) =>
  useUserData('ActiveProduct', {}, autoload)
export const useComparisonMarkets = (autoload) =>
  useUserData('ComparisonMarkets', {}, autoload)

export const useUserProducts = (autoload) => {
  const [value, set, load, loaded] = useUserData('UserProducts', [], autoload)
  return {products:value, setProducts:set, loadProducts:load, productsLoaded:loaded }
}

export const useUserMarkets = (autoload) => {
  const [markets, setMarkets, loadMarkets, marketsLoaded, addMarketItem, removeMarketItem] = useUserData(
    'UserMarkets',
    [],
    autoload,
    (a, b) => a.country_iso2_code === b.country_iso2_code
  )
  return { markets, setMarkets, loadMarkets, marketsLoaded, addMarketItem, removeMarketItem }
}
