import React from 'react'
import PropTypes from 'prop-types'

/* TODO merge with Fields/TextInput which is currently onChange don't pass parameter */
export const TextInput = ({
  disabled,
  id,
  name,
  handleChange,
  placeholder,
  type,
  value
}) => (
  <input
    className='great-mvp-field-input form-control'
    disabled={disabled}
    id={id}
    name={name}
    onChange={(e) => handleChange(e)}
    placeholder={placeholder}
    type={type}
    value={value}
  />
)

TextInput.propTypes = {
  disabled: PropTypes.bool,
  id: PropTypes.string,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string,
}

TextInput.defaultProps = {
  disabled: false,
  id: '',
  placeholder: 'Add some text',
  value: '',
  type: 'text'
}
