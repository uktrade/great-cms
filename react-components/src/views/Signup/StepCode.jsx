import React from 'react'
import PropTypes from 'prop-types'

import Field from '@src/components/Fields/Field'

export const StepCode = (props) => {
  return (
    <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
      { props.showTitle && <legend className="h-m text-blue-deep-80 body-l">Check your email</legend> }
      <p className="body-text great-mvp-synopsis m-t-0">We have emailed you a five-digit code. <br /> Enter it below:</p>
      <label htmlFor="id_code">Confirmation code</label>
      <Field
        id="id_code"
        type="text"
        placeholder="Enter code"
        name="code"
        disabled={props.disabled}
        value={props.code}
        handleChange={props.handleCodeChange}
        autofocus={true}
        errors={props.errors.code || []}
      />
      <button
        type="submit"
        id="signup-modal-submit-code"
        className="button button--primary m-t-s"
        disabled={props.disabled}
      >Submit</button>
    </form>
  )
}

StepCode.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  showTitle: PropTypes.bool,
}

StepCode.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
  showTitle: true,
}

export default StepCode
