/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Fields/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

import './stylesheets/StepCredentials.scss'


export default function StepCredentials(props){
  return (
    <div className='great-mvp-signup-wizard-step-credentials'>
      { props.showTitle && <h2 className="h-xl">Sign up</h2> }
      <p className="body-text m-t-0 m-b-m">
         <a href={Services.config.loginUrl} id="signup-modal-log-in">I already have a great.gov.uk account</a>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
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
        <p className='great-mvp-terms m-0'>By signing up, you agree to our <a href={Services.config.termsUrl} target="_blank" id="signup-modal-t-and-c">user agreement and privacy notice</a>.</p>
        <input
          type="submit"
          value="Sign up"
          id="signup-modal-submit"
          className="great-mvp-wizard-step-submit great-mvp-wizard-step-button m-t-m"
          disabled={props.disabled}
        />
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
    </div>
  )
}

StepCredentials.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string,
  googleUrl: PropTypes.string,
  linkedinUrl: PropTypes.string,
  showTitle: PropTypes.bool,
}

StepCredentials.defaultProps = {
  showTitle: true,
  disabled: false,
  errors: {},
  password: '',
  email: '',
}
