import Services from '@src/Services'
import actions from '@src/actions'
import { isObject, isArray, deepEqual } from '@src/Helpers'
import { useSelector } from 'react-redux'


const loading = {} // flag when data are being retrieved

// User settings items. These are async and the global state will get populated once complete
// default: is set on completion of retrieval is the object does not already exist
// defer: can be set to prevent the blob from loadind automatically. In that case, call the load method to initiate loading

export const useUserData = (blobName, defaultValue = [], autoload = true ) => {
  const blobValue = useSelector(
    (state) => state.userSettings && state.userSettings[blobName]
  )

  const saveBlob = (value) => Services.store.dispatch(actions.setUserData(blobName, value))

  const loadBlob = () => {
    if (!blobValue && !loading[blobName]) {
      loading[blobName] = 1
      Services.getUserData(blobName).then((result) => {
        const value = isObject(result) && (result[blobName] || defaultValue)
        saveBlob(value)
      })
    }
  }
  if(autoload) {
    loadBlob()
  }

  const addToList = (item) => {
  // Where the blob is a list, this method adds the given item to the end only if it's unique
    if(blobValue && isArray(blobValue)) {
      const duplicate = blobValue.reduce((out, cItem) => {
        const ret = out || deepEqual(cItem, item)
        return out || deepEqual(cItem, item)
      }, false
      )
      if(!duplicate) {
        saveBlob([...blobValue, item])
      }
    }
  }

  return [blobValue || defaultValue, saveBlob, loadBlob, addToList]
}

export const useUserProducts = (autoload) => useUserData('UserProducts', [], autoload)
export const useActiveProduct = (autoload) => useUserData('ActiveProduct', {}, autoload)
export const useComparisonMarkets = (autoload) => useUserData('ComparisonMarkets', {}, autoload)
export const useUserMarkets = (autoload) => {
  const [markets, setMarkets, loadMarkets, addMarketItem] = useUserData('UserMarkets', [], autoload)
  return {markets, setMarkets, loadMarkets, addMarketItem}
}
