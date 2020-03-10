import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'

import './stylesheets/Step.scss'


export default function Step1(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="h-xl p-b-s m-t-s">Business details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          label="Company name"
          name="company_name"
          disabled={props.disabled}
          value={props.value}
          handleChange={props.handleChange}
          autofocus={true}
          errors={props.errors.company_name || []}
        />
        <input
          type="submit"
          value="Continue"
          className="g-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

Step1.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  value: '',
}
