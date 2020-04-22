import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import Component from './Component'
import Services from '@src/Services'
import actions from '@src/actions'
import { getModalIsOpen, getCountriesExpertise } from '@src/reducers'


export function Container(props){

  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)

  function handleUpdateCompany() {
    setIsInProgress(true)
    setErrors({})
    Services.updateCompany({expertise_countries: props.countries.map(item => item.value)})
      .then(handleSubmitSuccess)
      .catch(handleSubmitError)
  }
  function handleSubmitSuccess(nextStep) {
    location.reload()
  }

  function handleSubmitError(errors) {
    setErrors(errors.message || errors)
    setIsInProgress(false)
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
      isInProgress={isInProgress}
      errors={errors}
      {...props}
    />
  )
}


const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'countries'),
    countries: getCountriesExpertise(state),
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