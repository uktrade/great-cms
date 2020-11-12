import React from 'react'
import PropTypes from 'prop-types'

import { FormGroup } from '../FormGroup'

export const Input = ({
  errors,
  label,
  disabled,
  id,
  type,
  placeholder,
  value,
  onChange,
  description,
  tooltip,
  example,
  readOnly,
  tabIndex,
  hideLabel
}) => (
  <FormGroup
    errors={errors}
    label={label}
    description={description}
    tooltip={tooltip}
    example={example}
    id={id}
    hideLabel={hideLabel}
  >
    <input
      className='form-control'
      id={id}
      type={type}
      name={id}
      disabled={disabled}
      onChange={(e) => onChange({[id]: e.target.value})}
      placeholder={placeholder}
      value={value}
      readOnly={readOnly}
      tabIndex={tabIndex}
    />
</FormGroup>
)

Input.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
  example: PropTypes.string,
  readOnly: PropTypes.bool,
  tabIndex: PropTypes.string,
  hideLabel: PropTypes.bool
}

Input.defaultProps = {
  errors: [],
  disabled: false,
  type: 'text',
  placeholder: '',
  value: '',
  description: '',
  tooltip: '',
  example: '',
  readOnly: false,
  tabIndex: '',
  hideLabel: false
}
