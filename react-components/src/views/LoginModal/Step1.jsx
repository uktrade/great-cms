import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Fields/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'
import ErrorList from '@src/components/ErrorList'

export default function Step1(props) {
  return (
    <>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          props.handleSubmit()
        }}
      >
        <legend className="h-m text-blue-deep-80 body-l">Log in</legend>
        <p>Do not have an account? <a href={Services.config.signupUrl} className='text-red-80 inline-block'>Sign up</a></p>
        <ErrorList errors={props.errors.__all__ || []} className="m-b-s" />
        <label htmlFor="id_email">Email address</label>
        <Field
          id="id_email"
          type="text"
          placeholder="Email address"
          name="email"
          disabled={props.disabled}
          value={props.email}
          handleChange={props.handleEmailChange}
          autofocus={true}
          errors={props.errors.email || []}
        />
        <label htmlFor="id_password" className='m-t-s'>Password</label>
        <Field
          id="id_password"
          type="password"
          placeholder="Password"
          name="password"
          disabled={props.disabled}
          value={props.password}
          handleChange={props.handlePasswordChange}
          errors={props.errors.password || []}
        />
        <a href={Services.config.passwordResetUrl} className='text-red-80 inline-block m-t-xs'>Forgotten password?</a>
        <br />
        <button
          type="submit"
          id="signup-modal-submit"
          className="button button--primary m-t-s"
          disabled={props.disabled}
        >Log in</button>
      </form>

      <div className="vertical-separator">
        <hr />
        <span>or</span>
        <hr />
      </div>

      <SocialLoginButtons linkedinUrl={props.linkedinLoginUrl} googleUrl={props.googleLoginUrl} />
    </>
  )
}

Step1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string
}

Step1.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  email: ''
}
