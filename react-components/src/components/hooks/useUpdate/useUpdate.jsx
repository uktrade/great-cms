import { useState } from 'react'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { analytics } from '@src/Helpers'

export const useUpdate = (field) => {
  const [pending, setPending] = useState(false)
  const [message, setMessage] = useState(false)
  const [errors, setErrors] = useState({})
  const debounceMessage = useDebounce(setMessage)

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
        setErrors(err.message || err)
      })
      .finally(() => {
        setPending(false)
        debounceMessage(false)
      })
  }

  const create = (object) => {
    setPending(true)
    return Services.apiModelObjectManage(object, 'POST')
      .catch((err) => {
        setErrors({ err })
      })
      .then((response) => response)
      .finally(() => {
        setPending(false)
        debounceMessage(false)
      })
  }

  return [update, create, message, pending, errors]
}
