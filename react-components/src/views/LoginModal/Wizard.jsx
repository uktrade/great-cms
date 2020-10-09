/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import Step1 from './Step1'


export default function Wizard(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [email, setEmail] = React.useState(props.email)
  const [password, setPassword] = React.useState(props.password)

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
  }

  function handleSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(nextStep)
  }

  function handleSubmit() {
    setErrors({})
    setIsInProgress(true)
    Services.checkCredentials({email, password})
      .then(() => location.assign(props.nextUrl))
      .catch(handleError)
  }

  const next = encodeURIComponent(`${location.origin}${props.nextUrl}`);
  const linkedinLoginUrl = `${Services.config.linkedInUrl}?next=${next}`
  const googleLoginUrl = `${Services.config.googleUrl}?next=${next}`

  return (
    <Step1
      disabled={isInProgress}
      errors={errors}
      handlePasswordChange={setPassword}
      handleSubmit={handleSubmit}
      handleEmailChange={setEmail}
      password={password}
      email={email}
      linkedinLoginUrl={linkedinLoginUrl}
      googleLoginUrl={googleLoginUrl}
    />
  )
 
}

Wizard.propTypes = {
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  email: PropTypes.string,
  password: PropTypes.string,
  nextUrl: PropTypes.string.isRequired,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  email: '',
  password: ''
}
