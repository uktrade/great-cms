/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Fields/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'
import ErrorList from '@src/components/ErrorList'
import './stylesheets/Step1.scss'


export default function Step1(props){
  return (
    <div className='great-mvp-signup-wizard-step-1'>
      <h2 className="h-xl m-t-l">Log in</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <ErrorList errors={props.errors.__all__ || []} className="m-b-s" />
        <Field
          type="text"
          placeholder="Email address"
          name="email"
          disabled={props.disabled}
          value={props.email}
          handleChange={props.handleEmailChange}
          autofocus={true}
          errors={props.errors.email || []}
        />
        <Field
          type="password"
          placeholder="Password"
          name="password"
          disabled={props.disabled}
          value={props.password}
          handleChange={props.handlePasswordChange}
          errors={props.errors.password || []}
        />
        <input
          type="submit"
          value="Log in"
          className="great-mvp-wizard-step-submit great-mvp-wizard-step-button"
          disabled={props.disabled}
        />
        <p><a href={Services.config.passwordResetUrl}>Forgotten password?</a></p>
      </form>

      <div className='great-mvp-vertical-separator'>
        <hr/>
        <span>or</span>
        <hr/>
      </div>

      <SocialLoginButtons
        linkedinUrl={props.linkedinLoginUrl}
        googleUrl={props.googleLoginUrl}
      />
      <p>Do not have an account? <a href={Services.config.signupUrl}>Sign up</a></p>
    </div>
  )
}

Step1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string,
}

Step1.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  email: '',
}
