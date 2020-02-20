import React from 'react'
import PropTypes from 'prop-types'

import Field from '@src/components/Field'

import './stylesheets/Step2.scss'


export default function Step2(props){
  return (
    <div className='great-mvp-signup-wizard-step-2'>
      <h2 className="h-xl">Confirmation code</h2>
      <p className="body-text great-mvp-synopsis">
        <span>we've emailed you a five-digit confirmation code.</span>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <Field
          type="text"
          placeholder="Enter code"
          name="code"
          disabled={props.disabled}
          value={props.code}
          handleChange={props.handleCodeChange}
          autofocus={true}
          errors={props.errors.code || []}
        />
        <input
          type="submit"
          value="Submit"
          className="great-mvp-wizard-step-submit"
          disabled={props.disabled}
        />
      </form>
    </div>
  )
}

Step2.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.array,
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
}

Step2.defaultProps = {
  code: '',
  disabled: false,
  errors: [],
}