import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'

import './stylesheets/Step.scss'


export default function StepSectors(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="great-mvp-wizard-step-heading">Business details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <AutoCompleteField
          label="What sectors are you interested in?"
          choices={Services.config.industryOptions}
          name="expertise_industries"
          disabled={props.disabled}
          value={props.value}
          handleChange={props.handleChange}
          autofocus={true}
          errors={props.errors.expertise_industries || []}
        />
        <input
          type="submit"
          value="Continue"
          className="great-mvp-wizard-step-submit g-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

StepSectors.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

StepSectors.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  value: '',
}
