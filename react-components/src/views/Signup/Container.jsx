import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

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
  const [errors, setErrors] = useState(props.errors)
  const [isInProgress, setIsInProgress] = useState(props.isInProgress)
  const [currentStep, setCurrentStep] = useState(props.currentStep)
  const [email, setEmail] = useState(props.email)
  const [password, setPassword] = useState(props.password)
  const [uidb64, setUidb64] = useState(props.uidb64)
  const [token, setToken] = useState(props.token)
  const [code, setCode] = useState('')

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
    Services.createUser({ email, password })
      .then((response) => response.json())
      .then((data) => {
        setUidb64(data.uidb64)
        setToken(data.token)
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
