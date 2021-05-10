import { useState } from 'react'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { analytics } from '@src/Helpers'

export const useUpdate = (field) => {
  const [pending, setPending] = useState(false)
  const [message, setMessage] = useState(false)
  const [errors, setErrors] = useState({})
  const debounceMessage = useDebounce(setMessage)
  const debounceErrorMessage = useDebounce(setErrors)

  const update = (data, section = '') => {
    setPending(true)
    return Services.apiModelObjectManage(data, 'PATCH')
      .then(() => {
        setMessage(true)
      })
      .then(() => {
        analytics({
          event: 'planSectionSaved',
          sectionTitle: field.replace(/_/g, '-'),
          sectionFormField: section,
        })
      })
      .catch((err) => {
        if (!window.navigator.onLine) {
          setErrors(
            {
              __all__: [
                'No internet, please checking the network cables, modem and router',
              ],
            } || err
          )
        } else {
          const errorMessage = {
            __all__: ['An unexpected error has occurred'],
          }
          setErrors(errorMessage || err)
        }
      })
      .finally(() => {
        setPending(false)
        debounceMessage(false)
        debounceErrorMessage([])
      })
  }

  const create = (object) => {
    setPending(true)
    return Services.apiModelObjectManage(object, 'POST')
      .catch((err) => {
        if (!window.navigator.onLine) {
          setErrors(
            {
              __all__: [
                'No internet, please checking the network cables, modem and router',
              ],
            } || err
          )
        } else {
          const errorMessage = {
            __all__: ['An unexpected error has occurred'],
          }
          setErrors(errorMessage || err)
        }
      })
      .then((response) => response)
      .finally(() => {
        setPending(false)
        debounceMessage(false)
        debounceErrorMessage([])
      })
  }

  const deleteItem = (data) => {
    setPending(true)
    return Services.apiModelObjectManage(data, 'DELETE')
      .catch((err) => {
        if (!window.navigator.onLine) {
          setErrors(
            {
              __all__: [
                'No internet, please checking the network cables, modem and router',
              ],
            } || err
          )
        } else {
          const errorMessage = {
            __all__: ['An unexpected error has occurred'],
          }
          setErrors(errorMessage || err)
        }
      })
      .finally(() => {
        setPending(false)
        debounceMessage(false)
        debounceErrorMessage([])
      })
  }

  return [update, create, deleteItem, message, errors, pending]
}
