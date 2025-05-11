import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'
import { analytics } from '@src/Helpers'
import { messages } from '@src/constants'

import {
  Signup,
  STEP_COMPLETE,
  STEP_VERIFICATION_CODE,
} from '@src/components/Signup'
import Services from '@src/Services'
import {
  getCountriesExpertise,
  getProductsExpertise,
  getNextUrl,
} from '@src/reducers'

export function Container(props) {
  const [message, setMessage] = useState(props.message)
  const [errors, setErrors] = useState(props.errors)
  const [isInProgress, setIsInProgress] = useState(props.isInProgress)
  const [currentStep, setCurrentStep] = useState(props.currentStep)
  const [email, setEmail] = useState(props.email)
  const [password, setPassword] = useState(props.password)
  const [uidb64, setUidb64] = useState(props.uidb64)
  const [token, setToken] = useState(props.token)
  const [code, setCode] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [termsAndConditions, setTermsAndConditions] = useState(props.termsAndConditions)
  const [isBgsSite] = useState(props.isBgsSite)

  function handleError(error) {
    // If verification code has expired
    if (Object.is(error, messages.MESSAGE_UNPROCESSABLE_ENTITY)) {
      setMessage('This confirmation code has expired. Check your email for a new code and enter it into the box below.')
    } else {
      setErrors(error.message || error)
    }
    setIsInProgress(false)
  }

  function handleSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(nextStep)
  }

  function handleStepCredentialsSubmit() {
    if (isBgsSite === true && !termsAndConditions) {
      setErrors({ terms_and_conditions: ['Tick the box to accept the terms and conditions'] })
      return
    }

    setErrors({})
    setMessage('')
    setIsInProgress(true)
    Services.createUser({ email, password, phoneNumber, next })
      .then((response) => response.json())
      .then((data) => {
        setUidb64(data.uidb64)
        setToken(data.token)
        analytics({
          event: 'signUp',
          referrerUrl: document.referrer,
          nextUrl: decodeURIComponent(next),
        })
      })
      .then(() => handleSuccess(STEP_VERIFICATION_CODE))
      .catch(handleError)
  }

  function handleStepCodeSubmit() {
    setErrors({})
    setIsInProgress(true)
    Services.checkVerificationCode({ uidb64, token, code })
      .then(() => handleSuccess(STEP_COMPLETE))
      .catch(handleError)
  }

  const next = encodeURIComponent(`${location.origin}${props.nextUrl}`)
  const linkedinLoginUrl = `${Services.config.linkedInUrl}?next=${next}`
  const googleLoginUrl = `${Services.config.googleUrl}?next=${next}`

  return (
    <Signup
      {...props}
      errors={errors}
      isInProgress={isInProgress}
      currentStep={currentStep}
      isBgsSite={isBgsSite}
      email={email}
      setEmail={setEmail}
      password={password}
      setPassword={setPassword}
      code={code}
      setCode={setCode}
      nextUrl={props.nextUrl}
      handleStepCredentialsSubmit={handleStepCredentialsSubmit}
      handleStepCodeSubmit={handleStepCodeSubmit}
      linkedinLoginUrl={linkedinLoginUrl}
      googleLoginUrl={googleLoginUrl}
      phoneNumber={phoneNumber}
      setPhoneNumber={setPhoneNumber}
      termsAndConditions={termsAndConditions}
      setTermsAndConditions={setTermsAndConditions}
      message={message}
    />
  )
}

const mapStateToProps = (state) => {
  return {
    products: getProductsExpertise(state),
    countries: getCountriesExpertise(state),
  }
}

const mapDispatchToProps = (dispatch) => {
  return {}
}

export const ConnectedContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Container)

export default function ({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>,
    element
  )
}
