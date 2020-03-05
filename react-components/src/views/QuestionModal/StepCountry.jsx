import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'

import './stylesheets/Step.scss'


export default function StepCountry(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="great-mvp-wizard-step-heading">Business details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <AutoCompleteField
          label="What country would you like to export to?"
          choices={Services.config.countryOptions}
          name="expertise_countries"
          disabled={props.disabled}
          value={props.value}
          handleChange={props.handleChange}
          autofocus={true}
          errors={props.errors.expertise_countries || []}
        />
        <input
          type="submit"
          value="Continue"
          className="great-mvp-wizard-step-submit"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

StepCountry.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

StepCountry.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  value: '',
}