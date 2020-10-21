import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

export default function Step1(props) {
  return (
    <>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          props.handleSubmit()
        }}
      >
        <legend className='h-s text-blue-deep-80 p-t-xs'>Log in</legend>
        <p className='m-b-xxs'>Do not have an account? <a href={Services.config.signupUrl} className='text-red-80 inline-block'>Sign up</a></p>
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
        <a href={Services.config.passwordResetUrl} className='text-red-80 inline-block'>Forgotten password?</a>
        <br />
        <button
          type='submit'
          id='signup-modal-submit'
          className='button button--primary m-t-s'
          disabled={props.disabled}
        >Log in</button>
      </form>

      <div className='vertical-separator'>
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
