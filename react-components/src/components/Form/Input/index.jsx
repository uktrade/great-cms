import React from 'react'
import PropTypes from 'prop-types'

import { FormGroup } from '../FormGroup'

export const Input = ({
  error,
  label,
  disabled,
  id,
  type,
  placeholder,
  value,
  onChange,
}) => (
  <FormGroup
    error={error}
  >
    <>
      <label className="form-label" htmlFor={id}>{label}</label>
      <input
        className='form-control'
        id={id}
        type={type}
        name={id}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        value={value}
      />
    </>
  </FormGroup>
)

Input.propTypes = {
  error: PropTypes.bool,
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired
}

Input.defaultProps = {
  error: false,
  disabled: false,
  type: 'text',
  placeholder: '',
  value: ''
}
