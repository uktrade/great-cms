import React from 'react'
import PropTypes from 'prop-types'

import './stylesheets/StepSuccess.scss'


export default function StepSuccess(props){
  return (
    <div className='great-mvp-signup-wizard-step-success p-h-xs' id="signup-modal-success">
      <h2 className="h-xl">Complete</h2>
      <p className='great-mvp-subtitle'>Your account has been created.</p>
      <div className="body-text great-mvp-synopsis m-t-0">
        <span>You can now:</span>
        <ul className="list list-bullet">
          <li>Start using your Great.gov.uk Dashboard</li>
          <li>Create an export plan</li>
          <li>Save your progress in learning</li>
        </ul>
      </div>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <input
          type="submit"
          value="Continue"
          id="signup-modal-submit-success"
          className="great-mvp-wizard-step-submit great-mvp-wizard-step-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}


StepSuccess.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
}
