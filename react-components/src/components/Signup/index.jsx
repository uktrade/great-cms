import React from 'react'
import PropTypes from 'prop-types'

import Form from './Form'
import Confirmation from './Confirmation'
import Complete from './Complete'

export const STEP_CREDENTIALS = 'credentials'
export const STEP_VERIFICATION_CODE = 'verification-code'
export const STEP_COMPLETE = 'complete'

const subHeadings = [
  'Compare international markets',
  'Create an export action plan',
  'Join the UK Export Academy',
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
          isBgsSite={props.isBgsSite}
          handlePhoneNumber={props.setPhoneNumber}
          linkedinLoginUrl={props.linkedinLoginUrl}
          googleLoginUrl={props.googleLoginUrl}
          handleSubmit={props.handleStepCredentialsSubmit}
          termsAndConditions={props.termsAndConditions}
          handleTermsAndConditionsChange={props.setTermsAndConditions}
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
    <div className="great signup">
      <div className="signup__info-panel signup-panel hide_image_below_1200">
        <div className="signup__info-panel__content">
          <h2 className="signup__info-panel__heading">Get exporting and grow your business</h2>
          <ul className="signup__info-panel__subheadings">
            {subHeadings.map((heading) => (
              <li key={heading}>
                <span role="img" className="great-icon fas fa-check-circle" aria-hidden="true" />
                <span>{heading}</span>
              </li>
            ))}
          </ul>

        </div>
      </div>
      <div className="signup__form-panel">

        {renderStep()}

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
