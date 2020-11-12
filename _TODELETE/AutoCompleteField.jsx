/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from '../react-components/src/components/ErrorList'
import FlagIcon from '../react-components/src/components/FlagIcon'

import Select, { components } from 'react-select'
import AsyncSelect from 'react-select/async';

import './stylesheets/AutoCompleteField.scss'


export function OptionWithFlag(props) {
  return (
    <components.Option {...props}>
      <FlagIcon code={props.data.value.toLowerCase()} />
      <span style={{paddingLeft: 10}}>{props.data.label} ({props.data.value})</span>
    </components.Option>
  )
}


export default function AutoCompleteField(props){

  const id_for_label = `id_${props.name}`
  const { errors, ...otherProps} = props;

  const handleChange = (values, { action, removedValue }) => props.handleChange(values || [])
  const getLabel = () => <label htmlFor={id_for_label} className='great-mvp-field-label'>{props.label}</label>

  const selectProps = {
    'className': 'great-mvp-autocomplete-field',
    'classNamePrefix': 'great-mvp-autocomplete-field',
    'id': id_for_label,
    'isClearable': true,
    'isMulti': true,
    'onChange': handleChange,
    ...otherProps,
  }

  return (
    <div>
      {props.label && getLabel()}
      <ErrorList errors={errors || []} />
      {selectProps.loadOptions ? <AsyncSelect {...selectProps} /> : <Select {...selectProps} />}
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
