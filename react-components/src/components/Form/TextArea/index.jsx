import React from 'react'
import PropTypes from 'prop-types'

import { FormGroup } from '../FormGroup'

export const TextArea = ({
  errors,
  label,
  disabled,
  id,
  placeholder,
  value,
  onChange,
  description,
  tooltip,
  example
}) => (
  <FormGroup
    errors={errors}
    label={label}
    description={description}
    tooltip={tooltip}
    example={example}
    id={id}
  >
    <textarea
      className='form-control'
      id={id}
      name={id}
      disabled={disabled}
      onChange={(e) => onChange({[id]: e.target.value})}
      placeholder={placeholder}
      value={value}
    />
  </FormGroup>
)

TextArea.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
  example: PropTypes.string,
}

TextArea.defaultProps = {
  errors: [],
  disabled: false,
  placeholder: '',
  value: '',
  description: '',
  tooltip: '',
  example: ''
}
