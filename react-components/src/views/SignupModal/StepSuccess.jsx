/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import './stylesheets/StepSuccess.scss'


export default function StepSuccess(props){
  return (
    <div className='great-mvp-signup-wizard-step-success p-h-xs' id="signup-modal-success">
      <h2 className="h-xl">Complete</h2>
      <p className='great-mvp-subtitle'>Your account has been created.</p>
      <div className="body-text great-mvp-synopsis m-t-0">
        <span>You can now:</span>
        <ul className="list list-bullet">
          <li>Start using your Great.gov.uk <a href={Services.config.dashboardUrl}>Dashboard</a></li>
          <li>Create an  <a href="/export-plan">export plan</a></li>
          <li>Save your progress in learning</li>
        </ul>
      </div>
      <a
        id="signup-modal-submit-success"
        className="great-mvp-wizard-step-submit great-mvp-wizard-step-button"
        href={props.nextUrl}
      >Continue</a>
    </div>
  )
}


StepSuccess.propTypes = {
  nextUrl: PropTypes.string.isRequired,
}
