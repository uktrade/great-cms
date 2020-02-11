import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './components/ErrorList'
import Field from './components/Field'

import './stylesheets/SignupWizardStep2.scss'


export default function SignupWizardStep2(props){
  return (
    <div className='great-mvp-signup-wizard-step-2'>
      <h2 className="heading-xlarge">Confirmation code</h2>
      <p className="body-text great-mvp-synopsis">
        <span>we've emailed you a five-digit confirmation code.</span>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <ErrorList errors={props.errors} />
        <Field
          type="number"
          placeholder="Enter code"
          name="code"
          disabled={props.disabled}
          value={props.code}
          handleChange={props.handleCodeChange}
          autofocus={true}
        />
        <input
          type="submit"
          value="Submit"
          className="button great-mvp-button great-mvp-submit"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

SignupWizardStep2.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
}

SignupWizardStep2.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
}