/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import Component from './Component'
import { getModalIsOpen, getIndustriesExpertise } from '@src/reducers'
import actions from '@src/actions'


export function Container(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [industries, setIndustries] = React.useState(props.industries)

  function handleIndustriesSubmit() {
    Services.updateCompany({expertise_industries: (industries || []).map(item => item.value)})
      .then(handleIndustriesSubmitSuccess)
      .catch(handleIndustriesSubmitError)
  }

  function handleIndustriesSubmitSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    window.location.reload()
  }

  function handleIndustriesSubmitError(errors) {
    setErrors(errors.message || errors)
    setIsInProgress(false)
  }

  return (
    <Component
      errors={errors}
      disabled={isInProgress}
      handleSubmit={handleIndustriesSubmit}
      handleChange={setIndustries}
      value={industries}
      industryOptions={Services.config.industryOptions}
      isOpen={props.isOpen}
      setIsOpen={props.setIsOpen}
    />
  )
}

Container.propTypes = {
  isOpen: PropTypes.bool,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  industries: PropTypes.array,
}

Container.defaultProps = {
  errors: {},
  isInProgress: false,
  industries: [],
}


const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'industries'),
    industries: getIndustriesExpertise(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('industries', isOpen))},
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
