import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'
import Select from 'react-select'

import './stylesheets/AutoCompleteField.scss'


export default function AutoCompleteField(props){

  const id_for_label = `id_${props.name}`

  function handleChange(values, { action, removedValue }) {
    props.handleChange(values)
  }

  function getLabel() {
    if (props.label) {
      return (
        <label htmlFor={id_for_label} className='great-mvp-field-label'>{props.label}</label>
      )
    }
  }

  return (
    <div>
      {getLabel()}
      <ErrorList errors={props.errors || []} />
      <Select
        id={id_for_label}
        options={props.choices}
        isMulti={true}
        isClearable={true}
        name={props.name}
        onChange={handleChange}
        value={props.value}
        autoFocus={props.autofocus}
        className='great-mvp-autocomplete-field'
        classNamePrefix='great-mvp-autocomplete-field'
        disabled={props.disabled}
        placeholder={props.placeholder}
      />
    </div>
  )
}
  

AutoCompleteField.propTypes = {
  type: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  autofocus: PropTypes.bool,
  errors: PropTypes.array,
}

AutoCompleteField.defaultProps = {
  autofocus: false,
  disabled: false,
  errors: [],
}
