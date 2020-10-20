import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

const StepCredentials = (props) => {
  return (
    <>
      <span className='beta bg-blue-deep-10 text-blue-deep-80'><strong>BETA</strong></span>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        { props.showTitle && <legend className='h-s text-blue-deep-80'>Sign up to great.gov.uk</legend> }
        <a href={Services.config.loginUrl} id='signup-modal-log-in' className='text-red-80 m-b-s inline-block'>I already have a great.gov.uk account</a>
        <Input
          label='Email address'
          id='email'
          placeholder='Email address'
          disabled={props.disabled}
          value={props.email}
          onChange={({email}) => props.handleEmailChange(email)}
          errors={props.errors.email || []}
        />
        <Input
          label='Password'
          id='password'
          type='password'
          placeholder='Password'
          disabled={props.disabled}
          value={props.password}
          onChange={({password}) => props.handlePasswordChange(password)}
          errors={props.errors.password || []}
        />
        <button
          type='submit'
          id='signup-modal-submit'
          className='button button--primary width-full m-b-s'
          disabled={props.disabled}
        >Sign up</button>
      </form>
      <p className='m-0'>By signing up, you agree to our <a href={Services.config.termsUrl} target='_blank' id='signup-modal-t-and-c' rel='noopener noreferrer' className='text-red-80'>user agreement</a> and <a href={Services.config.termsUrl} target='_blank' rel='noopener noreferrer' className='text-red-80'>privacy notice</a></p>
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
