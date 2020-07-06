import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'

import './stylesheets/Field.scss'


export function TextInput(props) {
  const { disabled, id, name, handleChange, placeholder, type, value } = props
  return (
    <input
      className='great-mvp-field-input form-control'
      disabled={disabled}
      id={id}
      name={name}
      onChange={(e) => handleChange(e.target.value)}
      placeholder={placeholder}
      type={type}
      value={value}
    />
  )
}

export function DateInput(props) {

  const { disabled, id, name, handleChange, placeholder } = props
  let { value } = props

  // date input doesn't like null values so convert to empty string here
  if (value === null) {
    value = ''
  }

  return (
    <input
      className='great-mvp-field-input form-control'
      disabled={disabled}
      id={id}
      name={name}
      onChange={(e) => handleChange(e)}
      placeholder={placeholder}
      type='date'
      value={value}
    />
  )
}

export function TextArea(props) {

  const { disabled, id, name, handleChange, placeholder, value } = props

  return (
    <textarea
      className="form-control"
      disabled={disabled}
      id={id}
      name={name}
      onChange={(e) => handleChange(e)}
      placeholder={placeholder}
      value={value}
    />
  )
}

export function RadioInput(props) {

  const { options, name, id, handleChange, value } = props

  const children = options.map(({label, val, disabled}, i) => {
    const childId = `${id}_${value}`
    return (
      <li key={i} className='multiple-choice'>
        <input
          type='radio'
          name={name}
          value={value}
          id={childId}
          disabled={disabled}
          checked={val === value}
          onChange={(e) => handleChange(e.target.value)}
        />
      <label id={`${id}_label`} htmlFor={childId} className='form-label'>{label}</label>
      </li>
    )
  })

  return <ul id={id} className='g-select-multiple '>{children}</ul>
}

export function FieldWithExample(props) {

  const id_for_label = `id_${props.name}`

  return (
    <>
      <label htmlFor={id_for_label} className='great-mvp-field-label'>{props.label}</label>
      <dl className='great-mvp-field-example'>
        <dt>Example</dt>
        <dd>{props.placeholder}</dd>
      </dl>
      <ErrorList errors={props.errors || []} />
      <TextArea
        id={id_for_label}
        {...props}
        placeholder='Add some text'
      />
    </>
  )
}

export default function Field(props){

  const { label, name, id } = props

  const idForLabel = `label_${name}`

  function getLabel() {
    if (label) {
      return (
        <label id={idForLabel} htmlFor={id} className='great-mvp-field-label'>{label}</label>
      )
    }
    return ''
  }

  function getInput() {
    const { type } = props

    if (type === 'radio') {
      return <RadioInput id={idForLabel} {...props} />
    }
    if (type === 'textarea') {
      return <TextArea id={idForLabel} {...props} />
    }
    if (type === 'date') {
      return <DateInput id={idForLabel} {...props} />
    }
    return <TextInput id={idForLabel} {...props} />
  }

  return (
    <>
      {getLabel()}
      <ErrorList errors={props.errors || []} />
      {getInput()}
    </>
  )
}


Field.propTypes = {
  type: PropTypes.string,
  placeholder: PropTypes.string,
  name: PropTypes.string.isRequired,
  label: PropTypes.string,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string,
  disabled: PropTypes.bool,
  autofocus: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  options: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
    disabled: PropTypes.bool,
  })),
  id: PropTypes.string
}

Field.defaultProps = {
  autofocus: false,
  disabled: false,
  label: '',
  errors: [],
  placeholder: '',
  value: '',
  options: [],
  type: '',
  id: '',
  disabled: false
}
