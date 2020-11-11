import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import Component, { STEP_COUNTRIES, STEP_START, STEP_SUCCESS } from './Component'
import Services from '@src/Services'
import actions from '@src/actions'
import { getModalIsOpen, getIndustriesExpertise } from '@src/reducers'


export function Container(props){

  const [errors, setErrors] = React.useState({})
  const [isInProgress, setIsInProgress] = React.useState(false)
  const [countries, setCountries] = React.useState([])
  const [currentStep, setCurrentStep] = React.useState(STEP_START)

  const handleGotoCountries = function () {
    setCurrentStep(STEP_COUNTRIES)
  }

  const handleSubmit = function() {
    if (Services.config.userIsAuthenticated) {
      handleUpdateExportPlan()
    } else {
      // todo: persis the user's answers after they sign up
      props.setIsSignupModalOpen(true)
    }
  }

  function handleUpdateExportPlan() {
    setIsInProgress(true)
    setErrors({})
    Services.updateExportPlan({target_markets: countries.map(item => item.label)})
      .then(handleSubmitSuccess)
      .catch(handleSubmitError)
  }

  function handleSubmitSuccess(nextStep) {
    setCurrentStep(STEP_SUCCESS)
    setIsInProgress(false)
  }

  function handleSubmitError(errors) {
    setErrors(errors.message || errors)
    setIsInProgress(false)
  }

  return (
    <Component
      handleGotoCountries={handleGotoCountries}
      handleSubmit={handleSubmit}
      isInProgress={isInProgress}
      setCountries={setCountries}
      countries={countries}
      errors={errors}
      currentStep={currentStep}
      {...props}
    />
  )
}


const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'countries'),
    industries: getIndustriesExpertise(state)
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('countries', isOpen))},
    setIsSignupModalOpen: isOpen => { dispatch(actions.toggleModalIsOpen('signup', isOpen))},
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