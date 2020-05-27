/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import StepCredentials from './StepCredentials'
import StepCode from './StepCode'
import StepSuccess from './StepSuccess'


export const STEP_CREDENTIALS = 'credentials'
export const STEP_VERIFICATION_CODE = 'verification-code'
export const STEP_COMPLETE = 'complete'


export default function Component(props){
  const asideTitle = (props.products.length > 0 || props.countries.length > 0) ? 'Sign up so we can save your settings' : ''

  function getAside() {
    if (props.products.length > 0 || props.countries.length > 0){
      return (
        <aside className='c-1-2'>
          <h2 className='h-l'>{ asideTitle }</h2>
          { props.products.length > 0 && <p className='p-xxs m-r-m'>{props.products.map((item, i) => <span key={i}>{item.label}</span>) }</p> }
          { props.countries.length > 0 && <p className='p-xxs m-r-m'>{props.countries.map((item, i) => <span key={i}>{item.label}</span>) }</p> }
        </aside>
      )      
    }
  }

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
          showTitle={props.showTitle}
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
          showTitle={props.showTitle}
        />
      )
    } else if (props.currentStep == STEP_COMPLETE) {
      return (
        <StepSuccess nextUrl={props.nextUrl} showTitle={props.showTitle} />
      )
    }
  }

  const aside = getAside()

  return (
    <div className='grid'>
      { aside }
      <div className={aside ? 'c-1-2' : 'c-full'}>
        {getStep()}
      </div>
    </div>
  )
}

Component.propTypes = {
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  currentStep: PropTypes.string,
  showTitle: PropTypes.bool,
  products: PropTypes.array,
  countries: PropTypes.array,

}

Component.defaultProps = {
  isInProgress: false,
  errors: {},
  companySettings: {},
  showTitle: true,
  products: [],
  countries: [],
}
