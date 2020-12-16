import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

export const Form = ({
  handleSubmit,
  showTitle,
  disabled,
  email,
  handleEmailChange,
  errors,
  password,
  handlePasswordChange,
  linkedinLoginUrl,
  googleLoginUrl
}) => (
  <>
    <span className='beta bg-blue-deep-10 text-blue-deep-80'><strong>BETA</strong></span>
    <form
      onSubmit={event => {
        event.preventDefault()
        handleSubmit()
      }}
    >
      { showTitle && <legend className='h-s text-blue-deep-80'>Sign up to great.gov.uk</legend> }
      <a href={Services.config.loginUrl} id='signup-modal-log-in' className='text-red-80 m-b-s inline-block'>I already have a great.gov.uk account</a>
      <Input
        label='Email address'
        id='email'
        type='email'
        placeholder='Email address'
        disabled={disabled}
        value={email}
        onChange={(item) => handleEmailChange(item.email)}
        errors={errors.email || []}
      />
      <Input
        label='Password'
        id='password'
        type='password'
        placeholder='Password'
        disabled={disabled}
        value={password}
        onChange={(item) => handlePasswordChange(item.password)}
        errors={errors.password || []}
      />
      <p className='m-0'>By signing up, you agree to our <a href={Services.config.termsUrl} target='_blank' id='signup-modal-t-and-c' rel='noopener noreferrer' className='text-red-80'>user agreement</a> and <a href={Services.config.termsUrl} target='_blank' rel='noopener noreferrer' className='text-red-80'>privacy notice</a></p>
      <button
        type='submit'
        id='signup-modal-submit'
        className='button button--primary width-full m-t-xs'
        disabled={disabled}
      >Sign up</button>
    </form>
    <div className='vertical-separator'>
      <hr className='bg-blue-deep-10'/>
      <span>or</span>
      <hr className='bg-blue-deep-10'/>
    </div>
    <SocialLoginButtons
      linkedinUrl={linkedinLoginUrl}
      googleUrl={googleLoginUrl}
      action='Sign up'
    />
  </>
)


Form.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.shape({
    email: PropTypes.arrayOf(PropTypes.string),
    password: PropTypes.arrayOf(PropTypes.string)
  }),
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string,
  linkedinLoginUrl: PropTypes.string.isRequired,
  googleLoginUrl: PropTypes.string.isRequired,
  showTitle: PropTypes.bool,
}

Form.defaultProps = {
  showTitle: true,
  disabled: false,
  errors: {},
  password: '',
  email: '',
}
