import React from 'react'
import PropTypes from 'prop-types'

import Services from './Services'
import ErrorList from './components/ErrorList'
import Field from './components/Field'
import SocialLoginButtons from './components/SocialLoginButtons'
import VerticalSeparator from './components/VerticalSeparator'

import './stylesheets/SignupWizardStep1.scss'


export default function SignupWizardStep1(props){
  return (
    <div className='great-mvp-signup-wizard-step-1'>
      <h2 className="heading-xlarge">Sign up</h2>
      <p className="body-text great-mvp-synopsis">
        <span>It's easier to sign up now and save your progress, already have an account? </span>
        <a href="#">Log in</a>
      </p>
      <SocialLoginButtons />
      <VerticalSeparator />
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <ErrorList errors={props.errors} />
        <Field
          type="text"
          placeholder="Email address"
          name="username"
          disabled={props.disabled}
          value={props.username}
          handleChange={props.handleUsernameChange}
          autofocus={true}
        />
        <Field
          type="password"
          placeholder="Password"
          name="password"
          disabled={props.disabled}
          value={props.password}
          handleChange={props.handlePasswordChange}
        />
        <p className='great-mvp-terms'>By clicking Sign up, you accept the <a href={Services.config.termsUrl} target="_blank">terms and conditions</a> of the great.gov.uk service.</p>
        <input
          type="submit"
          value="Sign up"
          className="button great-mvp-submit great-mvp-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

SignupWizardStep1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleUsernameChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  username: PropTypes.string,
}

SignupWizardStep1.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  username: '',
}