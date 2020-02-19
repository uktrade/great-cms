import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'
import VerticalSeparator from '@src/components/VerticalSeparator'

import './stylesheets/Step1.scss'


export default function Step1(props){
  return (
    <div className='great-mvp-signup-wizard-step-1'>
      <h2 className="h-xl">Sign up</h2>
      <p className="body-text great-mvp-synopsis">
        <span>It's easier to sign up now and save your progress, already have an account? </span>
        <a href="#">Log in</a>
      </p>
      <SocialLoginButtons />
      <VerticalSeparator />
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          placeholder="Email address"
          name="username"
          disabled={props.disabled}
          value={props.username}
          handleChange={props.handleUsernameChange}
          autofocus={true}
          errors={props.errors.username || []}
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
        <p className='great-mvp-terms'>By clicking Sign up, you accept the <a href={Services.config.termsUrl} target="_blank">terms and conditions</a> of the great.gov.uk service.</p>
        <input
          type="submit"
          value="Sign up"
          className="g-button great-mvp-submit great-mvp-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleUsernameChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  username: PropTypes.string,
}

Step1.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  username: '',
}