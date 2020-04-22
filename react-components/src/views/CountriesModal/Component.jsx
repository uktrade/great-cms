/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Modal from '@src/components/Modal'
import ErrorList from '@src/components/ErrorList'
import Services from '@src/Services'
import '@src/stylesheets/ModalCentreScreen.scss'

import StepCountries from './StepCountries'
import StepSuccess from './StepSuccess'

export const STEP_COUNTRIES = 'country'
export const STEP_SUCCESS = 'success'


export function SkipShowGenericContent(props) {
  return (
    <a
      href='#'
      className='great-mvp-wizard-step-link'
      onClick={event => { event.preventDefault(); props.onClick() }}
    >No thanks, I would like generic content</a>
  )
}


export default function Wizard(props){
  function getStep() {
    if (props.currentStep == STEP_COUNTRIES) {
      return (
        <StepCountries
          errors={props.errors}
          disabled={props.isInProgress}
          handleSubmit={props.handleSubmit}
          handleChange={props.setCountries}
          value={props.countries || []}
        />
      )
    } else if (props.currentStep == STEP_SUCCESS) {
      return (
        <StepSuccess
          successUrl={`${window.location}?success`}
          handleChangeAnswers={props.handleChangeAnswers}
          countries={props.countries}
          industries={Services.config.userIndustries || []}
          handleComplete={props.handleComplete}
        />
      )
    }
  }

  return (
    <Modal
      isOpen={props.isOpen}
      setIsOpen={props.setIsOpen}
      skipFeatureCookieName='skip-industries-of-interest'
      skipFeatureComponent={props.currentStep == STEP_COUNTRIES ? SkipShowGenericContent : null}
      performSkipFeatureCookieCheck={props.performSkipFeatureCookieCheck}
      id='dashboard-question-modal-lets-get-to-know-you'
      className='p-s'
      setIsOpen={props.setIsOpen}
    >
      <ErrorList errors={props.errors.__all__ || []} className='m-t-s' />
      {getStep()}
    </Modal>
  )
}

Wizard.propTypes = {
  isOpen: PropTypes.bool,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  industries: PropTypes.array,
  currentStep: PropTypes.string,
  performSkipFeatureCookieCheck: PropTypes.bool,
}

Wizard.defaultProps = {
  isOpen: false,
  errors: {},
  isInProgress: false,
  industries: [],
  currentStep: STEP_COUNTRIES,
  performSkipFeatureCookieCheck: true,
}

