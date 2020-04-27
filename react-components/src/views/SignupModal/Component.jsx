/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import Modal from '@src/components/Modal'

import Services from '@src/Services'
import StepCredentials from './StepCredentials'
import StepCode from './StepCode'
import StepSuccess from './StepSuccess'
import './stylesheets/Modal.scss'


export const STEP_CREDENTIALS = 'credentials'
export const STEP_VERIFICATION_CODE = 'verification-code'
export const STEP_COMPLETE = 'complete'


export function SkipShowGenericContent(props) {
  return (
    <div className="grid">
      <div className="c-1-2">
        &nbsp;
        <img src='/static/images/tourists.png' className="great-mvp-image-tourists" />
      </div>
      <div className="c-1-2">
        <a
          href='#'
          className='great-mvp-wizard-step-link m-t-l'
          onClick={event => { event.preventDefault(); props.onClick() }}
        >I don't want to sign up</a>
      </div>
    </div>
  )
}

export default function Component(props){
  const products = props.productsExpertise;
  const countries = props.countriesExpertise
  const asideTitle = (products.length > 0 || countries.length > 0) ? 'Sign up so we can save your settings' : ''

  function getStep() {
    if (props.currentStep == STEP_CREDENTIALS) {
      return (
        <StepCredentials
          errors={props.errors}
          disabled={props.isInProgress}
          handleSubmit={props.handleStepCredentialsSubmit}
          handleEmailChange={props.setEmail}
          handlePasswordChange={props.setPassword}
          email={props.email}
          password={props.password}
          linkedinLoginUrl={props.linkedinLoginUrl}
          googleLoginUrl={props.googleLoginUrl}
        />
      )
    } else if (props.currentStep == STEP_VERIFICATION_CODE) {
      return (
        <StepCode
          errors={props.errors}
          handleSubmit={props.handleStepCodeSubmit}
          disabled={props.isInProgress}
          handleCodeChange={props.setCode}
          code={props.code}
        />
      )
    } else if (props.currentStep == STEP_COMPLETE) {
      return (
        <StepSuccess handleSubmit={props.handleStepSuccessSubmit} />
      )
    }
  }

  return (
    <Modal
      isOpen={props.isOpen}
      setIsOpen={props.setIsOpen}
      id='signup-modal'
      skipFeatureCookieName='skip-signup'
      skipFeatureComponent={SkipShowGenericContent}
      performSkipFeatureCookieCheck={props.performSkipFeatureCookieCheck}
      className='ReactModal__Content--Signup p-l'
      preventClose={props.preventClose}
    >
      <div className="grid">
        <aside className="c-1-2">
          <h2 className="h-l">{ asideTitle }</h2>
          { products.length > 0 && <p className="p-xxs m-r-m">{products.map((item, i) => <span key={i}>{item.label}</span>) }</p> }
          { countries.length > 0 && <p className="p-xxs m-r-m">{countries.map((item, i) => <span key={i}>{item.label}</span>) }</p> }
        </aside>
        <div className="c-1-2">
          {getStep()}
        </div>
      </div>
    </Modal>
  )
}

Component.propTypes = {
  isOpen: PropTypes.bool,
  setIsOpen: PropTypes.func,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  currentStep: PropTypes.string,
  performSkipFeatureCookieCheck: PropTypes.bool,
  preventClose: PropTypes.bool,
}

Component.defaultProps = {
  isOpen: false,
  isInProgress: false,
  errors: {},
  companySettings: {},
  performSkipFeatureCookieCheck: true,
  preventClose: false,
}
