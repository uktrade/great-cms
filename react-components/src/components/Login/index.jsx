import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Form } from '@src/components/Login/Form'

export const Login = (props) => {
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [email, setEmail] = React.useState(props.email)
  const [password, setPassword] = React.useState(props.password)

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
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
    <Form
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

Login.propTypes = {
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  email: PropTypes.string,
  password: PropTypes.string,
  nextUrl: PropTypes.string.isRequired,
}

Login.defaultProps = {
  errors: {},
  isInProgress: false,
  email: '',
  password: ''
}
