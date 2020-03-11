import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import ErrorList from '@src/components/ErrorList'
import Services from '@src/Services'
import StepProgressBar from '@src/components/StepProgressBar';
import Step1 from './Step1'
import StepSectors from './StepSectors'
import StepCountry from './StepCountry'
import Step4 from './Step4'

import './stylesheets/Wizard.scss'


export const STEP_COMPANY_NAME = 'company-name'
export const STEP_SECTORS = 'sectors'
export const STEP_COUNTRIES = 'country'
export const STEP_PERSONAL_DETAILS = 'personal-details'
const PROGRESS_BAR_STEPS = [
  STEP_COMPANY_NAME,
  STEP_SECTORS,
  STEP_COUNTRIES,
  STEP_PERSONAL_DETAILS,
]

const FIELD_STEP_MAPPING = [
  ['company_name', STEP_COMPANY_NAME],
  ['expertise_industries', STEP_SECTORS],
  ['expertise_countries', STEP_COUNTRIES],
  ['first_name', STEP_PERSONAL_DETAILS],
  ['last_name', STEP_PERSONAL_DETAILS],
]

export default function Wizard(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [currentStep, setCurrentStep] = React.useState(props.currentStep)
  
  const [companyName, setCompanyName] = React.useState(props.companyName)
  const [industries, setIndustries] = React.useState(props.industries)
  const [countries, setCountries] = React.useState(props.countries)
  const [firstName, setFirstName] = React.useState(props.firstName)
  const [lastName, setLastName] = React.useState(props.lastName)

  function handleError(error) {
    setErrors(error.message || error)
    setIsInProgress(false)
  }

  function handleSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(nextStep)
  }

  function handeleApiUpdateError(errors) {
    setErrors(errors)
    for (let [fieldName, stepName] of FIELD_STEP_MAPPING) {
      if (errors[fieldName]) {
        setCurrentStep(stepName)
      }
    }
  }

  function handeleApiUpdateSuccess() {
    window.location.assign(`${window.location}?success`)
  }

  function handleIndustriesSubmit() {
    Services.enrolCompany({expertise_industries: industries.map(item => item.value)})
      .then(handeleApiUpdateSuccess)
      .catch(handeleApiUpdateError)
  }

  function handleUpdateCompany() {
    
    const data = {
      company_name: companyName,
      expertise_industries: industries.map(item => item.value),
      expertise_countries: countries.map(item => item.value),
      first_name: firstName,
      last_name: lastName,
    }

    Services.updateCompany(data)
      .then(handeleApiUpdateSuccess)
      .catch(handeleApiUpdateError)
  }

  function getStep() {
    if (currentStep == STEP_COMPANY_NAME) {
      return (
        <Step1
          errors={errors}
          disabled={isInProgress}
          handleSubmit={handleUpdateCompany}
          handleChange={setCompanyName}
          value={companyName}
        />
      )
    } else if (currentStep == STEP_SECTORS) {
      return (
        <StepSectors
          errors={errors}
          disabled={isInProgress}
          handleSubmit={handleIndustriesSubmit}
          handleChange={setIndustries}
          value={industries}
        />
      )
    } else if (currentStep == STEP_COUNTRIES) {
      return (
        <StepCountry
          errors={errors}
          disabled={isInProgress}
          handleSubmit={handleUpdateCompany}
          handleChange={setCountries}
          value={countries}
        />
      )
    } else if (currentStep == STEP_PERSONAL_DETAILS) {
      return (
        <Step4
          errors={errors}
          disabled={isInProgress}
          handleSubmit={handleUpdateCompany}
          handleFirstNameChange={setFirstName}
          handleLastNameChange={setLastName}
          firstNameValue={firstName}
          lastNameValue={lastName}
        />
      )
    }
  }

  return (
    <div className="great-mvp-modal">
      <h3 className="great-mvp-modal-title">Let’s get to know you</h3>
      <hr className="great-mvp-modal-title-line" />
      <ErrorList errors={errors.__all__ || []} className="m-t-s" />
      {getStep()}
    </div>
  )
}

Wizard.propTypes = {
  currentStep: PropTypes.number,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  username: PropTypes.string,
  password: PropTypes.string,
  industries: PropTypes.array,
  countries: PropTypes.array,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  currentStep: STEP_SECTORS,
  industries: [],
  countries: [],
}
