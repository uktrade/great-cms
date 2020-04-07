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


export function Base(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [countries, setCountries] = React.useState(Services.config.userCountries || [])
  const [currentStep, setCurrentStep] = React.useState(props.currentStep)

  function handleUpdateCompanies() {    
    const data = {expertise_countries: (countries || []).map(item => item.value)}
    Services.updateCompany(data)
      .then(handeleApiUpdateSuccess)
      .catch(handeleApiUpdateError)
  }

  function handeleApiUpdateError(errors) {
    setErrors(errors)
    setCurrentStep(STEP_COUNTRIES)
  }

  function handeleApiUpdateSuccess() {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(STEP_SUCCESS)
  }

  function getStep() {
    if (currentStep == STEP_COUNTRIES) {
      return (
        <StepCountries
          errors={errors}
          disabled={isInProgress}
          handleSubmit={handleUpdateCompanies}
          handleChange={setCountries}
          value={countries || []}
        />
      )
    } else if (currentStep == STEP_SUCCESS) {
      return (
        <StepSuccess
          successUrl={`${window.location}?success`}
          handleChangeAnswers={() => setCurrentStep(STEP_COUNTRIES)}
          countries={countries}
          industries={Services.config.userIndustries || []}
        />
      )
    }
  }

  return (
    <Modal
      isOpen={props.isOpen}
      skipFeatureCookieName='skip-industries-of-interest'
      skipFeatureComponent={currentStep == STEP_COUNTRIES ? SkipShowGenericContent : null}
      id='dashboard-question-modal-lets-get-to-know-you'
      className='p-s'
    >
      <ErrorList errors={errors.__all__ || []} className='m-t-s' />
      {getStep()}
    </Modal>
  )
}

Base.propTypes = {
  isOpen: PropTypes.bool,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  industries: PropTypes.array,
  currentStep: PropTypes.string,
}

Base.defaultProps = {
  isOpen: false,
  errors: {},
  isInProgress: false,
  industries: [],
  currentStep: STEP_COUNTRIES,
}


export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Base {...params} />, element)
}

