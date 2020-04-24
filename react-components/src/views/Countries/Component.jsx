import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Services from '@src/Services'
import Start from './Start'
import Success from './Success'
import Form from './Form'
import SuggestedCountries from './SuggestedCountries'
import ErrorList from '@src/components/ErrorList'

import './stylesheets/Component.scss'


export const STEP_COUNTRIES = 'countries'
export const STEP_SUCCESS = 'success'
export const STEP_START = 'start'


export default function Components(props){

  function getStep() {
    if (props.currentStep == STEP_START) {
      return <Start handleClick={props.handleGotoCountries} />
    } else if (props.currentStep == STEP_COUNTRIES) {
      return (
        <>
          <Form
            options={Services.config.countryOptions}
            handleSubmit={props.handleSubmit}
            handleChange={props.setCountries}
            value={props.countries}
            isInProgress={props.isInProgress}
            errors={props.errors}
          />
          {
            props.suggestedCountries.length > 0 && <SuggestedCountries
              suggestedCountries={props.suggestedCountries}
              countries={props.countries}
              industries={props.industries}
              handleClick={props.setCountries}
              disabled={props.isInProgress}
            />
          }
        </>
      )
    } else if (props.currentStep == STEP_SUCCESS) {
      return (
        <Success
          countries={props.countries}
          handleChangeAnswers={props.handleGotoCountries}
        />
      )
    }
  }

  return (
    <div className="great-mvp-countries container p-v-m">
      <div className="grid">
      <div className="c-1-5">&nbsp;</div>
        <div className="c-2-3 p-f-0">
          <ErrorList errors={props.errors.__all__ || []} className='m-t-s' />
          <p className="great-mvp-section-title m-b-s m-t-0">Export plan</p>
          {getStep()}
        </div>
      </div>
    </div>
  )
}

Components.propTypes = {
  suggestedCountries: PropTypes.array.isRequired,
  errors: PropTypes.object,
}

Components.defaultProps = {
  errors: {}
}

