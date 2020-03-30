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
  const { errors, ...otherProps} = props;

  return (
    <div>
      {getLabel()}
      <ErrorList errors={errors || []} />
      <Select
        className='great-mvp-autocomplete-field'
        classNamePrefix='great-mvp-autocomplete-field'
        id={id_for_label}
        isClearable={true}
        isMulti={true}
        onChange={handleChange}
        {...otherProps}
      />
    </div>
  )
}
  

AutoCompleteField.propTypes = {
  placeholder: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.array.isRequired,
  disabled: PropTypes.bool,
  autoFocus: PropTypes.bool,
  errors: PropTypes.array,
}

AutoCompleteField.defaultProps = {
  autoFocus: false,
  disabled: false,
  errors: [],
}
