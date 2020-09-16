import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Fields/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

const StepCredentials = (props) => {
  return (
    <>
      <span className='beta bg-blue-deep-10 text-blue-deep-80'><strong>BETA</strong></span>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        { props.showTitle && <legend className="h-m text-blue-deep-80 body-l">Sign up to great.gov.uk</legend> }
        <a href={Services.config.loginUrl} id="signup-modal-log-in" className='text-red-80 m-b-xs inline-block'>I already have a great.gov.uk account</a>

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
        <button
          type="submit"
          id="signup-modal-submit"
          className="button button--primary width-full m-v-s"
          disabled={props.disabled}
        >Sign up</button>
      </form>
      <p className='m-0'>By signing up, you agree to our <a href={Services.config.termsUrl} target="_blank" id="signup-modal-t-and-c" rel="noopener noreferrer" className='text-red-80'>user agreement</a> and <a href={Services.config.termsUrl} target="_blank" rel="noopener noreferrer" className='text-red-80'>privacy notice</a></p>
      <div className='vertical-separator'>
        <hr className='bg-blue-deep-10'/>
        <span>or</span>
        <hr className='bg-blue-deep-10'/>
      </div>
      <SocialLoginButtons
        linkedinUrl={props.linkedinLoginUrl}
        googleUrl={props.googleLoginUrl}
        action='Sign up'
      />
    </>
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
  linkedinLoginUrl: PropTypes.string.isRequired,
  googleLoginUrl: PropTypes.string.isRequired,
  showTitle: PropTypes.bool,
}

StepCredentials.defaultProps = {
  showTitle: true,
  disabled: false,
  errors: {},
  password: '',
  email: '',
}

export default StepCredentials
