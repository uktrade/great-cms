/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import StepCredentials from './StepCredentials'
import StepCode from './StepCode'
import StepSuccess from './StepSuccess'


export const STEP_CREDENTIALS = 0
export const STEP_VERIFICATION_CODE = 1
export const STEP_COMPLETE = 2

export default function Wizard(props){
  if (props.currentStep == STEP_CREDENTIALS) {
    return (
      <StepCredentials
        errors={props.errors}
        disabled={props.isInProgress}
        handleSubmit={props.handleStepCredentialsSubmit}
        handleEmailChange={props.setEmail}
        handlePasswordChange={props.setPassword}
        email={props.email}
        password={props.password}
        showLede={props.showCredentialsLede}
      />
    )
  } else if (props.currentStep == STEP_VERIFICATION_CODE) {
    return (
      <StepCode
        errors={props.errors}
        handleSubmit={props.handleStepCodeSubmit}
        disabled={props.isInProgress}
        handleCodeChange={props.setCode}
        code={props.code}
      />
    )
  } else if (props.currentStep == STEP_COMPLETE) {
    return (
      <StepSuccess handleSubmit={props.handleStepSuccessSubmit} />
    )
  }
}

Wizard.propTypes = {
  // props terminating here
  currentStep: PropTypes.number,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  email: PropTypes.string,
  password: PropTypes.string,
  nextUrl: PropTypes.string,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  currentStep: STEP_CREDENTIALS,
  email: '',
  password: '',
  nextUrl: /dashboard/,
}
