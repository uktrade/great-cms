import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { getMarkets } from '@src/reducers'
import { useSelector } from 'react-redux'

import ErrorList from '@src/components/ErrorList'
import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { Input } from '@src/components/Form/Input'
import Spinner from '@src/components/Spinner/Spinner'
import { sectionQuestionMapping, prependThe } from '@src/Helpers'
import { useUpdateExportPlan } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'

export const FormElements = memo(
  ({ formData: form, field, formFields, formGroupClassName }) => {
    const [formData, setFormData] = useState({ ...form })
    const [update, showMessage, pending, errors] = useUpdateExportPlan(field)
    const countriesWithThe = [
      'Central African Republic',
      'Comoros',
      'Czechia',
      'Dominican Republic',
      'Ivory Coast',
      'Maldives',
      'Marshall Islands',
      'Netherlands',
      'Philippines',
      'Solomon Islands',
      'United Arab Emirates',
      'United States',
    ]

    let country
    try {
      // this is to squash errors if we're not inside a provider
      country = useSelector((state) => getMarkets(state))
    } catch {}

    const substituteText = (str) =>
      (str || '').replace(
        '<country-name>',
        country ? prependThe(country.country_name) : 'your market'
      )

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
              hideLabel={item.hideLabel}
              id={item.name}
              label={substituteText(item.label)}
              placeholder={item.placeholder}
              value={formData[item.name]}
              onChange={handleChange}
              update={handleChange}
              tooltip={item.tooltip}
              example={item.example}
              description={substituteText(item.description)}
              key={item.name}
              prepend={item.currency ? item.currency : null}
              name={item.name}
              options={item.choices}
              type={fieldType === 'NumberInput' ? 'number' : 'text'}
              selected={formData[item.name]}
              lesson={item.lesson}
              formGroupClassName={formGroupClassName}
            />
          )
        })}
        {pending && <Spinner text="Saving..." />}
        {showMessage && <div role="status">Changes saved.</div>}
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
      tooltip: PropTypes.shape({
        content: PropTypes.string,
        title: PropTypes.string,
      }),
      hideLabel: PropTypes.bool,
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
