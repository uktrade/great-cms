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
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [currentStep, setCurrentStep] = React.useState(props.currentStep)
  const [email, setEmail] = React.useState(props.email)
  const [password, setPassword] = React.useState(props.password)
  const [code, setCode] = React.useState('')

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
  }

  function handleSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(nextStep)
  }

  function handleStepCredentialsSubmit() {
    setErrors({})
    setIsInProgress(true)
    Services.createUser({email, password})
      .then(() => handleSuccess(STEP_VERIFICATION_CODE))
      .catch(handleError)
  }

  function handleStepCodeSubmit(){
    setErrors({})
    setIsInProgress(true)
    Services.checkVerificationCode({email, code})
      .then(() => handleSuccess(STEP_COMPLETE))
      .catch(handleError)
  }

  function handleStepSuccessSubmit() {
    location.assign(props.nextUrl)
  }

  if (currentStep == STEP_CREDENTIALS) {
    return (
      <StepCredentials
        errors={errors}
        disabled={isInProgress}
        handleSubmit={handleStepCredentialsSubmit}
        handleEmailChange={setEmail}
        handlePasswordChange={setPassword}
        email={email}
        password={password}
        showLede={props.showCredentialsLede}
      />
    )
  } else if (currentStep == STEP_VERIFICATION_CODE) {
    return (
      <StepCode
        errors={errors}
        handleSubmit={handleStepCodeSubmit}
        disabled={isInProgress}
        handleCodeChange={setCode}
        code={code}
      />
    )
  } else if (currentStep == STEP_COMPLETE) {
    return (
      <StepSuccess handleSubmit={handleStepSuccessSubmit} />
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
  nextUrl: PropTypes.string.isRequired,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  currentStep: STEP_CREDENTIALS,
  email: '',
  password: ''
}
