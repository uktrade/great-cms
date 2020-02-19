import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'

import './stylesheets/Step.scss'



export default function Step4(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="great-mvp-wizard-step-heading">Personal details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          label="First name"
          name="first_name"
          disabled={props.disabled}
          value={props.firstNameValue}
          handleChange={props.handleFirstNameChange}
          autofocus={true}
          errors={props.errors.first_name || []}
        />
        <Field
          type="text"
          label="Last name"
          name="last_name"
          disabled={props.disabled}
          value={props.lastNameValue}
          handleChange={props.handleLastNameChange}
          errors={props.errors.last_name || []}
        />
        <input
          type="submit"
          value="Continue"
          className="great-mvp-wizard-step-submit"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step4.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleFirstNameChange: PropTypes.func.isRequired,
  handleLastNameChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  firstNameValuet: PropTypes.string,
  lastNameValuet: PropTypes.string,
}

Step4.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  firstNameValue: '',
  lastNameValue: '',
}