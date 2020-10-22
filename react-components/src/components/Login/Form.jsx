import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'
import ErrorList from '@src/components/ErrorList'

export const Form = ({
  handleSubmit,
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
    <form
      onSubmit={(event) => {
        event.preventDefault()
        handleSubmit()
      }}
    >
      <legend className='h-s text-blue-deep-80 p-t-xs'>Log in</legend>
      <p className='m-b-s'>Do not have an account? <a href={Services.config.signupUrl} className='text-red-80 inline-block'>Sign up</a></p>
      <ErrorList errors={errors.__all__ || []} className="m-b-s" />
      <Input
        label='Email address'
        id='email'
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
      <a href={Services.config.passwordResetUrl} className='text-red-80 inline-block'>Forgotten password?</a>
      <br />
      <button
        type='submit'
        id='signup-modal-submit'
        className='button button--primary button--full-width m-t-xs'
        disabled={disabled}
      >Log in</button>
    </form>

    <div className='vertical-separator'>
      <hr />
      <span>or</span>
      <hr />
    </div>
    <SocialLoginButtons linkedinUrl={linkedinLoginUrl} googleUrl={googleLoginUrl} />
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
  googleLoginUrl: PropTypes.string.isRequired
}

Form.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  email: ''
}
