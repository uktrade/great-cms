import { useState } from 'react'
import Services from '@src/Services'
import { analytics } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const useUpdateExportPlan = (field) => {
  const [pending, setPending] = useState(false)
  const [showMessage, setShowMessage] = useState(false)
  const [errors, setErrors] = useState({})
  const debounceMessage = useDebounce(setShowMessage)

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
        setErrors(err.message || err)
      })
      .finally(() => {
        setPending(false)
        debounceMessage(false)
      })
  }

  const update = useDebounce(request)

  return [update, showMessage, pending, errors]
}
