import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'

import './stylesheets/Step.scss'


export default function Step2(props){
  return (
    <div className="great-mvp-wizard-step">
      <h2 className="great-mvp-wizard-step-heading">Business details</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          label="What sectors are you interested in?"
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
          className="great-mvp-wizard-step-submit"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step2.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

Step2.defaultProps = {
  disabled: false,
  errors: [],
  password: '',
  value: '',
}