import Services from '@src/Services'
import actions from '@src/actions'
import { isObject, isArray, deepEqual, analytics } from '@src/Helpers'
import { useSelector } from 'react-redux'

const loading = {} // flag when data are being retrieved

// User settings items. These are async and the global state will get populated once complete
// default: is set on completion of retrieval is the object does not already exist
// autoload: can be set false to stop the blob from loading automatically. In that case, call the load method to initiate loading
// duplicateComparator: If a list, check for duplicates by calling this fn(a,b). Default is full deep comparison.

const useUserData = (
  blobName,
  defaultValue = [],
  autoload = true,
  context = 'Unknown context',
  duplicateComparator = deepEqual
) => {
  console.log("INVOKED useUserData: " + blobName + " " + autoload)
  const blobValue = useSelector(
    (state) => state.userSettings && state.userSettings[blobName]
  )

  const analyticsEvent = (item, addOrRemove, list) => {
    const eventConfig = {
      UserProducts: {
        name: 'Product',
        field: 'commodity_name',
        extra: { field: 'commodity_code', fieldName: 'Code' },
      },
      UserMarkets: { name: 'Market', field: 'country_name' },
    }[blobName]
    const pipeList = (fieldName) =>
      list.map((loopItem) => loopItem[fieldName]).join('|')
    if (eventConfig) {
      let event = {
        event: `${eventConfig.name.toLowerCase()}BasketEngagement`,
        [`basket${eventConfig.name}`]: item[eventConfig.field],
        [`basket${eventConfig.name}s`]: pipeList(eventConfig.field),
        [`addOrRemove${eventConfig.name}`]: addOrRemove,
        [`basket${eventConfig.name}Count`]: list.length,
        siteSection: context,
      }
      if (eventConfig.extra) {
        event = {
          ...event,
          [`basket${eventConfig.name}${eventConfig.extra.fieldName}s`]: pipeList(
            eventConfig.extra.field
          ),
          [`basket${eventConfig.name}${eventConfig.extra.fieldName}`]: item[
            eventConfig.extra.field
          ],
        }
      }
      analytics(event)
    }
  }

  const saveBlob = (value) =>
    Services.store.dispatch(actions.setUserData(blobName, value))

  const loadBlob = () => {
    if (!blobValue && !loading[blobName]) {
      loading[blobName] = 1
      Services.getUserData(blobName).then((result) => {
        const value = isObject(result) && (result[blobName] || defaultValue)
        saveBlob(value)
        loading[blobName] = 'loaded'
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
        const newList = [...blobValue, item]
        saveBlob(newList)
        analyticsEvent(item, 'add', newList)
      }
    }
  }

  const removeFromList = (item) => {
    // Where the blob is a list, this method removes the given item
    if (blobValue && isArray(blobValue)) {
      const index = blobValue.findIndex((cItem) =>
        duplicateComparator(cItem, item)
      )
      if (index >= 0) {
        const reduced = [...blobValue]
        reduced.splice(index, 1)
        saveBlob(reduced)
        analyticsEvent(item, 'remove', reduced)
      }
    }
  }

  console.log("EXITING useUserData: " + blobValue)
  return [
    blobValue || defaultValue,
    saveBlob,
    loadBlob,
    blobValue || loading[blobName] === 'loaded',
    addToList,
    removeFromList,
  ]
}

export const useActiveProduct = (autoload) =>
  useUserData('ActiveProduct', {}, autoload)
export const useComparisonMarkets = (autoload) =>
  useUserData('ComparisonMarkets', {}, autoload)

export const useUserProducts = (autoload, context) => {
  const [
    products,
    setProducts,
    loadProducts,
    productsLoaded,
    addProduct,
    removeProduct,
  ] = useUserData('UserProducts', [], autoload, context)
  return {
    products,
    setProducts,
    loadProducts,
    productsLoaded,
    addProduct,
    removeProduct,
  }
}

export const useUserMarkets = (autoload, context) => {
  const [
    markets,
    setMarkets,
    loadMarkets,
    marketsLoaded,
    addMarketItem,
    removeMarketItem,
  ] = useUserData(
    'UserMarkets',
    [],
    autoload,
    context,
    (a, b) => a.country_iso2_code === b.country_iso2_code
  )
  return {
    markets,
    setMarkets,
    loadMarkets,
    marketsLoaded,
    addMarketItem,
    removeMarketItem,
  }
}
