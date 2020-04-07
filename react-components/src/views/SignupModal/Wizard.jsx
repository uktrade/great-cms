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
      .then(onCodeSubmitSuccess)
      .catch(handleError)
  }

  function onCodeSubmitSuccess() {
    // company data may have been passed in at the start. Now the user has the 
    // login cookies the company can be created
    if (props.companySettings) {
      const data = {
        expertise_products_services: {
          // convert Array[{value: str, label: str}] to Array[str]
          other: props.companySettings.expertise_products_services.other.map(item => item.value),
        }
      }
      Services.updateCompany(data)
        .then(() => handleSuccess(STEP_COMPLETE))
        .catch(handleError)
    } else {
      handleSuccess(STEP_COMPLETE)
    }
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
