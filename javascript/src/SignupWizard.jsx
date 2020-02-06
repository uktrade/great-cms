import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import Services from './Services'
import SignupWizardStep1 from './SignupWizardStep1'
import SignupWizardStep2 from './SignupWizardStep2'
import SignupWizardStep3 from './SignupWizardStep3'


export const STEP_CREDENTIALS = 0
export const STEP_VERIFICATION_CODE = 1
export const STEP_COMPLETE = 2

export default function SignupWizard(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [currentStep, setCurrentStep] = React.useState(props.currentStep)
  const [username, setUsername] = React.useState(props.username)
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

  function handleStep1Submit() {
    setErrors({})
    setIsInProgress(true)
    Services.createUser({username, password})
      .then(() => handleSuccess(STEP_VERIFICATION_CODE))
      .catch(handleError)
  }

  function handleStep2Submit(){
    setErrors({})
    setIsInProgress(true)
    Services.checkVerificationCode({username, code})
      .then(() => handleSuccess(STEP_COMPLETE))
      .catch(handleError)
  }

  function handleStep3Submit() {
    location.reload()
  }

  if (currentStep == STEP_CREDENTIALS) {
    return (
      <SignupWizardStep1
        errors={errors}
        disabled={isInProgress}
        handleSubmit={handleStep1Submit}
        handleUsernameChange={setUsername}
        handlePasswordChange={setPassword}
        username={username}
        password={password}
      />
    )
  } else if (currentStep == STEP_VERIFICATION_CODE) {
    return (
      <SignupWizardStep2
        errors={errors}
        handleSubmit={handleStep2Submit}
        disabled={isInProgress}
        handleCodeChange={setCode}
        code={code}
      />
    )
  } else if (currentStep == STEP_COMPLETE) {
    return (
      <SignupWizardStep3
        handleSubmit={handleStep3Submit}
      />
    )
  }
}

SignupWizard.propTypes = {
  // props terminating here
  currentStep: PropTypes.number,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  username: PropTypes.string,
  password: PropTypes.string,
}

SignupWizard.defaultProps = {
  errors: {},
  isInProgress: false,
  currentStep: STEP_CREDENTIALS,
  username: '',
  password: ''
}