import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Form } from '@src/components/Login/Form'

export const Login = ({ nextUrl, ...props }) => {
  /* eslint-disable react/destructuring-assignment */
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [email, setEmail] = React.useState(props.email)
  const [password, setPassword] = React.useState(props.password)

  /* eslint-enable react/destructuring-assignment */

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
  }

  const getRedirectUrl = ({ token, uidb64 }) => {
    // if new verification token generated, means user exists but is unverified
    // redirect to verification code step of signup

    // account for when there are existing query parameters in URL (e.g. ?next=/dashboard/)
    const queryParamConnector = window.location.search ? '&' : '?'

    const { signupUrl } = Services.config

    return (
      token && uidb64
        ? `${signupUrl}${queryParamConnector}uidb64=${uidb64}&token=${token}`
        : nextUrl
    )
  }

  function handleSubmit() {
    setErrors({})
    setIsInProgress(true)
    Services.checkCredentials({ email, password })
      .then((response) => response.json())
      // eslint-disable-next-line no-restricted-globals
      .then((data) => location.assign(getRedirectUrl(data)))
      .catch(handleError)
  }

  // eslint-disable-next-line no-restricted-globals
  const next = encodeURIComponent(`${location.origin}${nextUrl}`)
  const linkedinLoginUrl = `${Services.config.linkedInUrl}?next=${next}`
  const googleLoginUrl = `${Services.config.googleUrl}?next=${next}`

  return (
    <div className="signup">
      <div className="signup__form-panel">
        <a href="/" className="inline-block">
          <img
            className="m-f-auto m-r-auto signup__logo"
            src="/static/images/dit_logo_335x160.png"
            alt="Department for International Trade"
            width="335"
            height="160"
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
      <div className="signup__info-panel">
        <div className="signup__info-panel__content">
          <h1>
            Sign in to continue your exporting journey
          </h1>
          <p className="body-l">Don&apos;t have an account?</p>
          <a
            href={Services.config.signupUrl}
            className="button secondary-button"
          >
            Sign up
          </a>
        </div>
        <img src="/static/images/signin-image.png" alt="" className='background-image' />
      </div>
    </div>
  )
}

const filterProps = obj => Object.fromEntries(Object.entries(obj).filter(([key]) => key.includes('LoginUrl')))

Login.propTypes = {
  ...filterProps(Form.propTypes),
  isInProgress: PropTypes.bool,
  nextUrl: PropTypes.string.isRequired,
}

Login.defaultProps = {
  ...filterProps(Form.defaultProps),
  isInProgress: false,
}
