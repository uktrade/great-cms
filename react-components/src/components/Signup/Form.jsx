import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import SocialLoginButtons from '@src/components/SocialLoginButtons'

const SHOW_SOCIAL_LOGIN = false

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
  phoneNumber,
  handlePhoneNumber,
}) => (
  <form
    onSubmit={(event) => {
      event.preventDefault()
      handleSubmit()
    }}
    className="signup__form"
    autoComplete="new-off"
  >
    {showTitle && (
      <h1 className="govuk-heading-m govuk-!-margin-top-8 govuk-!-margin-bottom-6">
        Create an account
      </h1>
    )}


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
      label="UK telephone number (optional)"
      info="By providing your phone number, you agree to be contacted by DBT to gather feedback on your experiences of great.gov.uk."
      infoClassName="g-panel govuk-body-s govuk-!-margin-top-2 govuk-!-margin-bottom-2"
      descriptionClassName="govuk-body-s"
      id="phone_number"
      type="tel"
      disabled={disabled}
      value={phoneNumber || ''}
      onChange={(item) => handlePhoneNumber(item.phone_number)}
      errors={errors.mobile_phone_number || []}
    />
    <Input
      label="Password"
      id="password"
      type="password"
      description="Your password must have at least 10 characters, including letters and numbers."
      descriptionClassName= 'govuk-!-margin-bottom-1 great-font-main great-line-height-30 great-font-size-18 govuk-body-l great-text-dark-grey'
      disabled={disabled}
      value={password}
      onChange={(item) => handlePasswordChange(item.password)}
      errors={errors.password || []}
      isPasswordShowHide={true}
    />
    <p className="signup__conditions">
      By signing up, you agree to our{' '}
      <a href="/terms-and-conditions/">terms and conditions</a> and{' '}
      <a href="/privacy/">privacy notice</a>
    </p>
    <button
      type="submit"
      id="signup-modal-submit"
      className="govuk-button govuk-!-margin-top-1 great-width-auto"
      disabled={disabled}
    >
      Create Account
    </button>
    {SHOW_SOCIAL_LOGIN && (
      <>
        <div className="govuk-!-margin-top-4 govuk-!-margin-bottom-4">
          <hr className="bg-blue-deep-10" />
          <span>or</span>
          <hr className="bg-blue-deep-10" />
        </div>
        <SocialLoginButtons
          linkedinUrl={linkedinLoginUrl}
          googleUrl={googleLoginUrl}
          action="Sign up"
        />
      </>
    )}
     <p className="govuk-!-margin-bottom-6 govuk-!-margin-top-0">
      Already have an account?{' '}
      <a
        href={Services.config.loginUrl} id="signup-modal-log-in"
      >
        Sign in
      </a>
    </p>
  </form>
)

Form.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.shape({
    email: PropTypes.arrayOf(PropTypes.string),
    password: PropTypes.arrayOf(PropTypes.string),
    mobile_phone_number: PropTypes.arrayOf(PropTypes.string),
  }),
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleEmailChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  email: PropTypes.string,
  phoneNumber: PropTypes.string,
  handlePhoneNumber: PropTypes.func.isRequired,
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
  phoneNumber: null,
}

export default Form
