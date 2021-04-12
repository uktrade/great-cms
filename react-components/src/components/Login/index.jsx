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

  return (<div className="bg-red-60 signup signup--reverse signup__container">
    <div className="signup__steps-panel">
      <a href="/">
        <img
          className="m-f-auto m-r-auto signup__logo"
          src="/static/images/logo-filled.svg"
          alt="Exporting is Great"
          width="148"
          height="69"
        />
      </a>
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
    </div>
    <div className="signup__right-panel">
      <div className="signup__right-panel__headings">
        <h1>Sign in to continue your exporting journey</h1>
        <p>Don't have an account?</p>
        <a href={Services.config.signupUrl} className="button">Sign up</a>
      </div>
      <img src="/static/images/sign-in.png" alt="" />
    </div>
  </div>)

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
