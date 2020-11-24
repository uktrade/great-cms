import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import Component, { STEP_SUCCESS, STEP_COUNTRIES } from './Component'
import Services from '@src/Services'
import actions from '@src/actions'
import { getModalIsOpen, getCountriesExpertise, getPerformFeatureSKipCookieCheck } from '@src/reducers'


export function Container(props){
  const [errors, setErrors] = React.useState()
  const [isInProgress, setIsInProgress] = React.useState()
  const [currentStep, setCurrentStep] = React.useState()

  function handleUpdateCompany() {    
    const data = {expertise_countries: (props.countries || []).map(item => item.value)}
    Services.updateCompany(data)
      .then(handeleApiUpdateSuccess)
      .catch(handeleApiUpdateError)
  }

  function handeleApiUpdateError(apiErrors) {
    setErrors(apiErrors)
    gotoCountries()
  }

  function handeleApiUpdateSuccess() {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(STEP_SUCCESS)
  }

  function gotoCountries() {
    setCurrentStep(STEP_COUNTRIES)
  }

  function handleComplete() {
    window.location.reload()
  }

  const handleSubmit = function() {
    if (Services.config.userIsAuthenticated) {
      handleUpdateCompany()
    } else {
      props.setIsSignupModalOpen(true)
    }
  }

  return (
    <Component
      handleSubmit={handleSubmit}
      errors={errors}
      isInProgress={isInProgress}
      currentStep={currentStep}
      handleChangeAnswers={gotoCountries}
      handleComplete={handleComplete}
      {...props}
    />
  )
}

const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'countries'),
    countries: getCountriesExpertise(state),
    performSkipFeatureCookieCheck: getPerformFeatureSKipCookieCheck(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('countries', isOpen))},
    setIsSignupModalOpen: isOpen => { dispatch(actions.toggleModalIsOpen('signup', isOpen))},
    setCountries: countries => { dispatch(actions.setCountriesExpertise(countries)) },
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