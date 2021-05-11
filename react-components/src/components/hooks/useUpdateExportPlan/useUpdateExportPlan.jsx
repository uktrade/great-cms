import { useState } from 'react'
import Services from '@src/Services'
import { analytics } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const unexpectedError =
  'An unexpected error has occurred. Please reload the page and try again.'
export const connectionError =
  'You’re offline. Reconnect to save your progress and continue'

export const useUpdateExportPlan = (field) => {
  const [pending, setPending] = useState(false)
  const [showMessage, setShowMessage] = useState(false)
  const [errors, setErrors] = useState({})
  const debounceMessage = useDebounce(setShowMessage)
  const debounceErrorMessage = useDebounce(setErrors)

  const request = (data, section = '') => {
    setPending(true)
    return Services.updateExportPlan(data)
      .then(() => {
        setShowMessage(true)
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
              __all__: [connectionError],
            } || err
          )
        } else {
          const errorMessage = {
            __all__: [unexpectedError],
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

  const update = useDebounce(request)

  return [update, showMessage, pending, errors]
}
