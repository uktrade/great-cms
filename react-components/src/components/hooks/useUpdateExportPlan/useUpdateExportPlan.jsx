import { useState } from 'react'
import Services from '@src/Services'
import { analytics } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'

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

  const update = useDebounce(request)

  return [update, showMessage, pending, errors]
}
