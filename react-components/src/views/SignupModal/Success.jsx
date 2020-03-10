import React from 'react'
import PropTypes from 'prop-types'

import './stylesheets/Success.scss'


export default function Step3(props){
  return (
    <div className='great-mvp-signup-wizard-step-3'>
      <h2 className="h-xl">Complete</h2>
      <p className='great-mvp-subtitle'>Your account has been created.</p>
      <div className="body-text great-mvp-synopsis">
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
          className="great-mvp-wizard-step-submit g-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}


Step3.PropTypes = {
  handleSubmit: PropTypes.func.isRequired,
}
