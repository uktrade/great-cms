/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import { connect, Provider } from 'react-redux'

import Component, { STEP_COMPLETE, STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from './Component'
import Services from '@src/Services'
import actions from '@src/actions'
import { getCountriesExpertise, getModalIsOpen, getPerformFeatureSKipCookieCheck, getProductsExpertise, getNextUrl } from '@src/reducers'


export function Container(props){

  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [currentStep, setCurrentStep] = React.useState(STEP_CREDENTIALS)
  const [email, setEmail] = React.useState(props.email)
  const [password, setPassword] = React.useState(props.password)
  const [code, setCode] = React.useState('')

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
  }

  function handleSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(nextStep)
  }

  function handleStepCredentialsSubmit() {
    setErrors({})
    setIsInProgress(true)
    Services.createUser({email, password})
      .then(() => handleSuccess(STEP_VERIFICATION_CODE))
      .catch(handleError)
  }

  function handleStepCodeSubmit(){
    setErrors({})
    setIsInProgress(true)
    Services.checkVerificationCode({email, code})
      .then(onCodeSubmitSuccess)
      .catch(handleError)
  }

  function onCodeSubmitSuccess() {
    // company data may have been passed in at the start. Now the user has the 
    // login cookies the company can be created
    
    if (props.productsExpertise.length > 0 || props.countriesExpertise.length > 0) {
      const data = {
          expertise_products_services: {other: props.productsExpertise.map(item => item.value)},
          expertise_countries: props.countriesExpertise,
      }
      Services.updateCompany(data)
        .then(() => handleSuccess(STEP_COMPLETE))
        .catch(handleError)
    } else {
      handleSuccess(STEP_COMPLETE)
    }
  }

  function handleStepSuccessSubmit() {
    location.assign(props.nextUrl)
  }

  const next = encodeURIComponent(`${location.origin}${props.nextUrl}`);
  const linkedinLoginUrl = `${Services.config.linkedInUrl}?next=${next}`
  const googleLoginUrl = `${Services.config.googleUrl}?next=${next}`

  return (
    <Component
      {...props}
      errors={errors}
      isInProgress={isInProgress}
      currentStep={currentStep}
      email={email}
      setEmail={setEmail}
      password={password}
      setPassword={setPassword}
      code={code}
      setCode={setCode}
      handleStepSuccessSubmit={handleStepSuccessSubmit}
      handleStepCredentialsSubmit={handleStepCredentialsSubmit}
      handleStepCodeSubmit={handleStepCodeSubmit}
      linkedinLoginUrl={linkedinLoginUrl}
      googleLoginUrl={googleLoginUrl}
    />
  )
}


const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'signup'),
    productsExpertise: getProductsExpertise(state),
    countriesExpertise: getCountriesExpertise(state),
    performSkipFeatureCookieCheck: getPerformFeatureSKipCookieCheck(state),
    nextUrl: getNextUrl(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('signup', isOpen))},
  }
}

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(Container)

export default function({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>,
    element
  )
}