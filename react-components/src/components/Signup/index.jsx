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
  "Create an export plan that's right for your business",
]

export const Signup = (props) => {
  const { errors, disabled, email, showTitle, isInProgress } = props
  const asideTitle =
    props.products.length > 0 || props.countries.length > 0
      ? 'Sign up so we can save your settings'
      : ''

  function getAside() {
    if (props.products.length > 0 || props.countries.length > 0) {
      return (
        <aside className="c-1-2">
          <h2 className="h-l">{asideTitle}</h2>
          {props.products.length > 0 && (
            <p className="p-xxs m-r-m">
              {props.products.map((item, i) => (
                <span key={i}>{item.label}</span>
              ))}
            </p>
          )}
          {props.countries.length > 0 && (
            <p className="p-xxs m-r-m">
              {props.countries.map((item, i) => (
                <span key={i}>{item.label}</span>
              ))}
            </p>
          )}
        </aside>
      )
    }
  }

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
          linkedinLoginUrl={props.linkedinLoginUrl}
          googleLoginUrl={props.googleLoginUrl}
          handleSubmit={props.handleStepCredentialsSubmit}
        />
      )
    } else if (props.currentStep === STEP_VERIFICATION_CODE) {
      return (
        <Confirmation
          {...sharedStepProps}
          handleSubmit={props.handleStepCodeSubmit}
          handleCodeChange={props.setCode}
          code={props.code}
        />
      )
    } else if (props.currentStep === STEP_COMPLETE) {
      return <Complete nextUrl={props.nextUrl} showTitle={props.showTitle} />
    }
  }

  return (
    <div className="bg-blue-deep-80 signup signup__container">
      <div className="signup__steps-panel">
        <a href="/">
          <img
            className="m-f-auto m-r-auto signup__logo"
            src="/static/images/dit_logo_335x160.png"
            alt=""
            width="148"
            height="71"
          />
        </a>
        {renderStep()}
        <p className="g-panel signup__questions-panel">
          If you have any questions or feedback please{' '}
          <a href="/contact/feedback/" target="_blank">
            get in touch
          </a>
        </p>
      </div>
      <div className="signup__right-panel">
        <div className="signup__right-panel__headings">
          <h1>Find new customers around the world</h1>
          {subHeadings.map((heading) => (
            <div className="signup__right-panel__subheadings" key={heading}>
              <i className="fas fa-check-circle" aria-hidden="true"></i>
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
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  currentStep: PropTypes.string,
  showTitle: PropTypes.bool,
  products: PropTypes.array,
  countries: PropTypes.array,
}

Signup.defaultProps = {
  isInProgress: false,
  errors: {},
  companySettings: {},
  showTitle: true,
  products: [],
  countries: [],
}
