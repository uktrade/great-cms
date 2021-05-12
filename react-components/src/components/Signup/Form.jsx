import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

const Form = ({
  handleSubmit,
  showTitle,
  disabled,
  email,
  handleEmailChange,
  errors,
  password,
  handlePasswordChange,
  linkedinLoginUrl,
  googleLoginUrl,
}) => (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        handleSubmit()
      }}
      className="signup__form"
    >
      {showTitle && (
        <legend className="h-s text-blue-deep-80 p-t-xs">Create an account</legend>
      )}
      Already have an account? &nbsp;&nbsp;
      <a
        href={Services.config.loginUrl}
        id="signup-modal-log-in"
        className="text-red-80 m-b-s inline-block"
      >
        Sign in
      </a>
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
      <p className="signup__conditions">
        By signing up, you agree to our <a href="/terms-and-conditions/">terms and conditions</a> and{' '}
        <a href="/privacy-and-cookies/">privacy notice</a>
      </p>
      <button
        type="submit"
        id="signup-modal-submit"
        className="button button--primary width-full m-t-xs"
        disabled={disabled}
      >
        Sign up
      </button>
      <div className="vertical-seperator">
        <hr className="bg-blue-deep-10" />
        <span>or</span>
        <hr className="bg-blue-deep-10" />
      </div>
      <SocialLoginButtons
        linkedinUrl={linkedinLoginUrl}
        googleUrl={googleLoginUrl}
        action="Sign up"
      />

    </form>
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
  showTitle: PropTypes.bool,
}

Form.defaultProps = {
  showTitle: true,
  disabled: false,
  errors: {},
  password: '',
  email: '',
}

export default Form
