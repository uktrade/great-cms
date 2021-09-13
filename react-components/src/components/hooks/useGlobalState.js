import Services from '@src/Services'
import actions from '@src/actions'
import { isObject, isArray, deepEqual } from '@src/Helpers'
import { useSelector } from 'react-redux'

// User settings items. These are async and the global state will get populated once complete
// default: is set on completion of retrieval is the object does not already exist
// autoload: can be set false to stop the blob from loading automatically. In that case, call the load method to initiate loading
// duplicateComparator: If a list, check for duplicates by calling this fn(a,b). Default is full deep comparison.

export const useGlobalState = (
  blobName,
  defaultValue = [],
) => {
  const blobValue = useSelector(
    (state) => state.globalState && state.globalState[blobName]
  )

  const saveBlob = (value) =>
    Services.store.dispatch(actions.setGlobalValue(blobName, value))

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

  return [blobValue || defaultValue, saveBlob]
}
