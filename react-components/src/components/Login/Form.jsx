import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'
import ErrorList from '@src/components/ErrorList'

const SHOW_SOCIAL_LOGIN = false

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
      <h3 className="govuk-heading-m govuk-!-margin-top-8 govuk-!-margin-bottom-6 great-width-auto">Sign in</h3>

      {/* eslint-disable-next-line no-underscore-dangle,react/prop-types */}
      <ErrorList errors={errors.__all__ || []} className="govuk-!-margin-bottom-2" />
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
        isPasswordShowHide={true}
      />
      <a
        href={Services.config.passwordResetUrl}
        className="inline-block govuk-!-margin-bottom-4"
      >
        Forgotten password?
      </a>
      <br />
      <button
        type="submit"
        id="signup-modal-submit"
        className="govuk-button great-border-bottom-black govuk-!-margin-top-1 great-width-auto"
        disabled={disabled}
      >
        Sign in
      </button>
      {SHOW_SOCIAL_LOGIN && (
        <>
          <div className="vertical-seperator">
            <hr className="bg-blue-deep-10" />
            <span>or</span>
            <hr className="bg-blue-deep-10" />
          </div>
          <SocialLoginButtons
            linkedinUrl={linkedinLoginUrl}
            googleUrl={googleLoginUrl}
            action="Sign in"
          />
        </>
      )}
      <p className="govuk-!-margin-bottom-2 govuk-!-margin-top-0">
        Don&apos;t have an account?{' '}
        <a
          href={Services.config.signupUrl}
        >
          Sign up
        </a>
      </p>
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
