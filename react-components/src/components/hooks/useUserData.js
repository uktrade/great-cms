import Services from '@src/Services'
import actions from '@src/actions'
import { isObject } from '@src/Helpers'
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

  return [blobValue || defaultValue, saveBlob, loadBlob]
}

export const useUserProducts = (autoload) => useUserData('UserProducts', [], autoload)
export const useActiveProduct = (autoload) => useUserData('ActiveProduct', {}, autoload)
export const useUserMarkets = (autoload) => useUserData('UserMarkets', [], autoload)
export const useComparisonMarkets = (autoload) => useUserData('ComparisonMarkets', {}, autoload)
