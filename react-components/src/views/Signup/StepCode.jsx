/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Field from '@src/components/Fields/Field'

import './stylesheets/StepCode.scss'


export default function StepCode(props){
  return (
    <div className='great-mvp-signup-wizard-step-code'>
      { props.showTitle && <h2 className="h-xl">Confirmation code</h2> }
      <p className="body-text great-mvp-synopsis m-t-0">
        <span>we've emailed you a five-digit confirmation code.</span>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          placeholder="Enter code"
          name="code"
          disabled={props.disabled}
          value={props.code}
          handleChange={props.handleCodeChange}
          autofocus={true}
          errors={props.errors.code || []}
        />
        <input
          type="submit"
          value="Submit"
          id="signup-modal-submit-code"
          className="great-mvp-wizard-step-submit great-mvp-wizard-step-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

StepCode.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  showTitle: PropTypes.bool,
}

StepCode.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
  showTitle: true,
}
