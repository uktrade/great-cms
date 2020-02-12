import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'

import '../stylesheets/Field.scss'


export default function Field(props){

  function handleChange(event) {
    props.handleChange(event.target.value)
  }

  return (
    <div className="form-group great-mvp-field">
      <ErrorList errors={props.errors || []} />
      <input
        type={props.type}
        placeholder={props.placeholder}
        name={props.name}
        className="form-control"
        value={props.value}
        onChange={handleChange}
        disabled={props.disabled}
        autoFocus={props.autofocus}
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
