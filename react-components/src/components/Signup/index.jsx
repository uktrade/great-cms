import React from 'react'
import PropTypes from 'prop-types'

import Form from './Form'
import Confirmation from './Confirmation'
import Complete from './Complete'

export const STEP_CREDENTIALS = 'credentials'
export const STEP_VERIFICATION_CODE = 'verification-code'
export const STEP_COMPLETE = 'complete'

const subHeadings = [
  'Learn how to sell abroad',
  'Find the best country for your product',
  'Create an export plan that\'s right for your business',
]

export const Signup = (props) => {
  const { errors, disabled, email, showTitle, isInProgress, message } = props

  const sharedStepProps = {
    errors,
    disabled,
    email,
    showTitle,
    isInProgress,
    message,
  }

  function renderStep() {
    if (props.currentStep === STEP_CREDENTIALS) {
      return (
        <Form
          {...sharedStepProps}
          handleEmailChange={props.setEmail}
          handlePasswordChange={props.setPassword}
          password={props.password}
          phoneNumber={props.phoneNumber}
          handlePhoneNumber={props.setPhoneNumber}
          linkedinLoginUrl={props.linkedinLoginUrl}
          googleLoginUrl={props.googleLoginUrl}
          handleSubmit={props.handleStepCredentialsSubmit}
        />
      )
    }

    if (props.currentStep === STEP_VERIFICATION_CODE) {
      return (
        <Confirmation
          {...sharedStepProps}
          handleSubmit={props.handleStepCodeSubmit}
          handleCodeChange={props.setCode}
          code={props.code}
        />
      )
    }

    if (props.currentStep === STEP_COMPLETE) {
      return <Complete nextUrl={props.nextUrl} showTitle={props.showTitle} />
    }

    return null
  }

  return (
    <div className="signup">
      <div className="signup__form-panel">
        <a href="/" className="inline-block">
          <img
            className="m-f-auto m-r-auto signup__logo"
            src="/static/images/dbt_logo_335x160.png"
            alt="Department for Business and Trade"
          />
        </a>

        {renderStep()}

        <p id="get-in-touch" className="g-panel body-m">
          If you have any questions or feedback please{' '}
          <a href="/contact/feedback/" target="_blank">
            get in touch
          </a>
        </p>
      </div>
      <div className="signup__info-panel signup-panel">
        <div class="great-logo">
          </div>
        <div className="signup__info-panel__content">
          <h1>Find new customers around the world</h1>
          <ul className="signup__info-panel__subheadings">
            {subHeadings.map((heading) => (
              <li key={heading}>
                <span role="img" className="fas fa-check-circle" aria-hidden="true" />
                <span>{heading}</span>
              </li>
            ))}
          </ul>

        </div>
      </div>
    </div>
  )
}

Signup.propTypes = {
  ...Form.propTypes,
  isInProgress: PropTypes.bool,
  currentStep: PropTypes.oneOf([STEP_CREDENTIALS, STEP_COMPLETE, STEP_VERIFICATION_CODE]),
  showTitle: PropTypes.bool,
  message: PropTypes.string,
}

Signup.defaultProps = {
  ...Form.defaultProps,
  isInProgress: false,
  currentStep: STEP_CREDENTIALS,
  showTitle: true,
  message: '',
}
