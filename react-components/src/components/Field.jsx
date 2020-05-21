import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'

import './stylesheets/Field.scss'


export function TextInput(props) {

  const { disabled, id, name, handleChange, placeholder, type, value, autofocus } = props

  return (
    <input
      autoFocus={autofocus}
      className='great-mvp-field-input form-control'
      disabled={disabled}
      id={id}
      name={name}
      onChange={() => handleChange(event.target.value)}
      placeholder={placeholder}
      type={type}
      value={value}
    />
  )
}

export function TextArea(props) {

  const { disabled, id, name, handleChange, placeholder, type, value } = props

  return (
    <textarea
      className="form-control"
      disabled={disabled}
      id={id}
      name={name}
      onChange={(e) => handleChange(e)}
      placeholder={placeholder}
      type={type}
      value={value}
    />
  )
}

export function RadioInput(props) {

  const { options, name, value, handleChange, id } = props

  const children = options.map(({label, optionValue, disabled}) => {
    const fieldId = `${id}_${optionValue}`
    return (
      <li key={label} className='multiple-choice'>
        <input
          type='radio'
          name={name}
          value={optionValue}
          id={fieldId}
          disabled={disabled}
          checked={optionValue === value}
          onChange={() => handleChange(event.target.value)}
        />
      <label id={`${fieldId}_label`} htmlFor={fieldId} className='form-label'>{label}</label>
      </li>
    )
  })

  return <ul id={id} className='g-select-multiple '>{children}</ul>
}

export default function Field(props){

  const { type, errors, name, label } = props

  const idForLabel = `id_${name}`

  function getLabel() {
    if (label) {
      return (
        <label htmlFor={idForLabel} className='great-mvp-field-label'>{label}</label>
      )
    }
    return ''
  }

  function getInput() {

    if (type === 'radio') {
      return <RadioInput id={idForLabel} {...props} />
    }
    if (type === 'textarea') {
      return <TextArea id={idForLabel} {...props} />
    }
    return <TextInput id={idForLabel} {...props} />
  }

  return (
    <div>
      {getLabel()}
      <ErrorList errors={errors || []} />
      {getInput()}
    </div>
  )
}


Field.propTypes = {
  type: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  disabled: PropTypes.bool,
  autofocus: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  options: PropTypes.arrayOf(PropTypes.string),
}

Field.defaultProps = {
  autofocus: false,
  disabled: false,
  errors: [],
  placeholder: '',
  label: '',
  options: [],
  value: ''
}
