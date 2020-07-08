import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './ErrorList'

import './stylesheets/Field.scss'


export function TextInput(props) {
  return (
    <input
      autoFocus={props.autofocus}
      className='great-mvp-field-input form-control'
      disabled={props.disabled}
      id={props.id}
      name={props.name}
      onChange={() => props.handleChange(event.target.value)}
      placeholder={props.placeholder}
      type={props.type}
      value={props.value}
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

  const children = props.options.map(({label, value, disabled}, i) => {
    const id = `${props.id}_${value}`
    return (
      <li key={i} className='multiple-choice'>
        <input
          type='radio'
          name={props.name}
          value={value}
          id={id}
          disabled={disabled}
          checked={value === props.value}
          onChange={() => props.handleChange(event.target.value)}
        />
        <label id={`{$id}_label`} htmlFor={id} className='form-label'>{label}</label>
      </li>
    )
  })

  return <ul id={props.id} className='g-select-multiple '>{children}</ul>
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

  const id_for_label = `id_${props.name}`

  function getLabel() {
    if (props.label) {
      return (
        <label htmlFor={id_for_label} className='great-mvp-field-label'>{props.label}</label>
      )
    }
  }

  function getInput() {
    if (props.type === 'radio') {
      return <RadioInput id={id_for_label} {...props} />
    }
    if (props.type === 'textarea') {
      return <TextArea id={id_for_label} {...props} />
    }
    return <TextInput id={id_for_label} {...props} />
  }

  return (
    <div>
      {getLabel()}
      <ErrorList errors={props.errors || []} />
      {getInput()}
    </div>
  )
}


Field.propTypes = {
  type: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
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
  placeholder: '',
}
