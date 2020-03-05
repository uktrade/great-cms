import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'

import './stylesheets/Step.scss'


export default function Step3(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="great-mvp-wizard-step-heading">Business details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          label="What country would you like to export to?"
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
          className="great-mvp-wizard-step-submit g-button"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step3.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

Step3.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  value: '',
}
