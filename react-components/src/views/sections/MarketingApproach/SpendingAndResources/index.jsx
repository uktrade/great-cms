import React, { useState } from 'react'
import PropTypes from 'prop-types'

import FieldWithExample from '@src/components/Fields/FieldWithExample'
import Services from '../../../../Services'

export const SpendingAndResources = ({
  field,
  formFields,
  formData,
}) => {

  const [input, setInput] = useState(formData)

  const update = (e) => {
    setInput({[e.target.name]: e.target.value})
    Services.updateExportPlan({ [field]: {[e.target.name]: e.target.value}} )
      .then(() => {})
      .catch(() => {})
  }

  return (
    <>
      {formFields.map(item => (
        <FieldWithExample
          tooltip={item.tooltip}
          label={item.label}
          example={item.example}
          key={item.name}
          name={item.name}
          value={input[item.name]}
          description={item.description}
          placeholder={Number.isInteger(item.placeholder) ? item.placeholder : 'Add some text'}
          currency={item.currency}
          tag={Number.isInteger(item.placeholder) ? 'number' : 'text'}
          handleChange={update}
        />
      ))}
    </>
  )
}

SpendingAndResources.propTypes = {
  field: PropTypes.string.isRequired,
  formData: PropTypes.objectOf(PropTypes.string).isRequired,
  formFields: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    placeholder: PropTypes.string.isRequired,
  })).isRequired,
}
