import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'

import './stylesheets/Field.scss'


export default function Field(props){

  const id_for_label = `id_${props.name}`

  function handleChange(event) {
    props.handleChange(event.target.value)
  }

  function getLabel() {
    if (props.label) {
      return (
        <label htmlFor={id_for_label} className="great-mvp-field-label">{props.label}</label>
      )
    }
  }

  return (
    <div>
      {getLabel()}
      <ErrorList errors={props.errors || []} />
      <input
        autoFocus={props.autofocus}
        className="great-mvp-field-input form-control"
        disabled={props.disabled}
        id={id_for_label}
        name={props.name}
        onChange={handleChange}
        placeholder={props.placeholder}
        type={props.type}
        value={props.value}
      />
    </div>
  )
}


Field.propTypes = {
  type: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  autofocus: PropTypes.bool,
  errors: PropTypes.array,
}

Field.defaultProps = {
  autofocus: false,
  disabled: false,
  errors: [],
}
