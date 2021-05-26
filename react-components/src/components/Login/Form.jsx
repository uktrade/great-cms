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
  googleLoginUrl,
}) => (
  <>
    <form
      className="signup__form"
      onSubmit={(event) => {
        event.preventDefault()
        handleSubmit()
      }}
    >
      <legend className="h-s text-blue-deep-80 p-t-xs">Sign in</legend>
      <p className="m-b-s">
        Don't have an account?{' '}
        <a
          href={Services.config.signupUrl}
          className="text-red-80 inline-block"
        >
          Sign up
        </a>
      </p>
      <ErrorList errors={errors.__all__ || []} className="m-b-s" />
      <Input
        label="Email address"
        id="email"
        type="email"
        disabled={disabled}
        value={email.toLowerCase()}
        onChange={(item) => handleEmailChange(item.email)}
        errors={errors.email || []}
      />
      <Input
        label="Password"
        id="password"
        type="password"
        disabled={disabled}
        value={password}
        onChange={(item) => handlePasswordChange(item.password)}
        errors={errors.password || []}
      />
      <a
        href={Services.config.passwordResetUrl}
        className="text-red-80 inline-block"
      >
        Forgotten password?
      </a>
      <br />
      <button
        type="submit"
        id="signup-modal-submit"
        className="button button--primary button--full-width m-t-xs"
        disabled={disabled}
      >
        Sign in
      </button>
      {false && (
        <div className="vertical-seperator">
          <hr className="bg-blue-deep-10" />
          <span>or</span>
          <hr className="bg-blue-deep-10" />
        </div>
      )}
      {false && (
        <SocialLoginButtons
          linkedinUrl={linkedinLoginUrl}
          googleUrl={googleLoginUrl}
          action="Sign in"
        />
      )}
    </form>
  </>
)

Form.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.shape({
    email: PropTypes.arrayOf(PropTypes.string),
    password: PropTypes.arrayOf(PropTypes.string),
  }),
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string,
  linkedinLoginUrl: PropTypes.string.isRequired,
  googleLoginUrl: PropTypes.string.isRequired,
}

Form.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  email: '',
}
