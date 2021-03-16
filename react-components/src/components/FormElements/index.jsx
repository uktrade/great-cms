import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { Input } from '@src/components/Form/Input'
import Spinner from '@src/components/Spinner/Spinner'
import { getLabel, sectionQuestionMapping } from '@src/Helpers'
import { useUpdateExportPlan } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'

export const FormElements = memo(
  ({ formData: form, field, formFields, formGroupClassName }) => {
    const [formData, setFormData] = useState({ ...form })
    const [update, showMessage, pending, errors] = useUpdateExportPlan(field)

    const handleChange = (e) => {
      const data = {
        ...formData,
        ...e,
      }

      setFormData(data)
      update({ [field]: data }, sectionQuestionMapping[Object.keys(e)[0]])
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
              tooltip={item.tooltip}
              example={item.example}
              description={item.description}
              key={item.name}
              prepend={item.currency ? item.currency : null}
              name={item.name}
              options={item.choices}
              type={fieldType === 'NumberInput' ? 'number' : 'text'}
              selected={
                formData[item.name] && item.choices
                  ? getLabel(item.choices, formData[item.name])
                  : ''
              }
              lesson={item.lesson}
              formGroupClassName={formGroupClassName}
            />
          )
        })}
        {pending && <Spinner text="Saving..." />}
        {showMessage && 'Changes saved.'}
        <ErrorList errors={errors.__all__ || []} className="m-0" />
      </>
    )
  }
)

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
  formGroupClassName: PropTypes.string,
}

FormElements.defaultProps = {
  formGroupClassName: '',
}
