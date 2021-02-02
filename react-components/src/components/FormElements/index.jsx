import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { Input } from '@src/components/Form/Input'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import Spinner from '@src/components/Spinner/Spinner'
import { analytics, sectionQuestionMapping } from '@src/Helpers'

export const FormElements = memo(({ formData: form, field, formFields }) => {
  const [formData, setFormData] = useState({ ...form })
  const [pending, setPending] = useState(false)
  const [showMessage, setShowMessage] = useState(false)
  const [errors, setErrors] = useState({})
  const debounceMessage = useDebounce(setShowMessage)

  const update = (data, section = '') => {
    Services.updateExportPlan({ [field]: data })
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

  const debounceUpdate = useDebounce(update)

  const handleChange = (e) => {
    const data = {
      ...formData,
      ...e,
    }

    setFormData(data)
    setPending(true)
    debounceUpdate(data, sectionQuestionMapping[Object.keys(e)[0]])
  }

  return (
    <>
      {formFields.map((item) => {
        const fieldType = item.field_type
        let Component
        if (fieldType === 'NumberInput') {
          Component = Input
        } else {
          Component = fieldType === 'Select' ? Select : TextArea
        }

        return (
          <Component
            id={item.name}
            label={item.label}
            placeholder={item.placeholder}
            value={formData[item.name]}
            onChange={handleChange}
            update={handleChange}
            tooltip={{
              content: item.tooltip,
            }}
            example={{
              content: item.example,
            }}
            description={item.description}
            key={item.name}
            prepend={item.currency ? item.currency : null}
            name={item.name}
            options={item.choices}
            type={fieldType === 'NumberInput' ? 'number' : 'text'}
            selected={
              formData[item.name] && item.choices
                ? item.choices.find((x) => x.value === formData[item.name])
                    .label
                : ''
            }
          />
        )
      })}
      {pending && <Spinner text="Saving..." />}
      {showMessage && 'Changes saved.'}
      <ErrorList errors={errors.__all__ || []} className="m-0" />
    </>
  )
})

FormElements.propTypes = {
  formFields: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      placeholder: PropTypes.string.isRequired,
      field_type: PropTypes.string.isRequired,
    })
  ).isRequired,
  field: PropTypes.string.isRequired,
  formData: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  ).isRequired,
}
