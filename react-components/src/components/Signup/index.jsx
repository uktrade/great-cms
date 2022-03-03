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
  const { errors, disabled, email, showTitle, isInProgress } = props

  const sharedStepProps = {
    errors,
    disabled,
    email,
    showTitle,
    isInProgress,
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
    <div className="bg-blue-deep-80 signup signup--reverse signup__container">
      <div className="signup__steps-panel">
        <a href="/" className="inline-block">
          <img
            className="m-f-auto m-r-auto signup__logo"
            src="/static/images/dit_logo_335x160.png"
            alt="Department for International Trade"
            width="335"
            height="160"
          />
        </a>

        {renderStep()}

        <p className="g-panel body-m">
          If you have any questions or feedback please{' '}
          <a href="/contact/feedback/" target="_blank">
            get in touch
          </a>
        </p>
      </div>
      <div className="signup__right-panel">
        <div className="signup__right-panel__headings">
          <h2>Find new customers around the world</h2>
          {subHeadings.map((heading) => (
            <div className="signup__right-panel__subheadings" key={heading}>
              <i className="fas fa-check-circle" aria-hidden="true" />
              <p>{heading}</p>
            </div>
          ))}
        </div>

        <img
          className="m-f-auto m-r-auto"
          src="/static/images/sign-up-illustration.svg"
          alt=""
        />
      </div>
    </div>
  )
}

Signup.propTypes = {
  ...Form.propTypes,
  isInProgress: PropTypes.bool,
  currentStep: PropTypes.oneOf([STEP_CREDENTIALS, STEP_COMPLETE, STEP_VERIFICATION_CODE]),
  showTitle: PropTypes.bool,
}

Signup.defaultProps = {
  ...Form.defaultProps,
  isInProgress: false,
  currentStep: STEP_CREDENTIALS,
  showTitle: true,
}
