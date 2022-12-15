import React from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'

const Confirmation = ({
  handleSubmit,
  showTitle,
  disabled,
  code,
  handleCodeChange,
  errors,
  message,
}) => (
  <form
    className="signup__confirmation"
    onSubmit={(event) => {
      event.preventDefault()
      handleSubmit()
    }}
  >
    <i className="fas fa-info-circle" aria-hidden="true" />

    {showTitle && (
      <legend className="h-s text-blue-deep-80 p-t-xs">Check your email</legend>
    )}
    <p className="m-b-s">
    We&#39;ve sent a code to your email address. Don&#39;t forget to check your spam folder if you can&#39;t see it. <br /> Enter the code below to complete registration:
    </p>
    <Input
      label="Confirmation code"
      id="code"
      placeholder="Enter code"
      disabled={disabled}
      value={code}
      onChange={(item) => handleCodeChange(item.code)}
      errors={errors.code || []}
      message={message}
    />
    <button
      type="submit"
      id="signup-modal-submit-code"
      className="button button--primary m-t-0 width-full"
      disabled={disabled}
    >
      Submit
    </button>
  </form>
)

Confirmation.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.shape({
    code: PropTypes.arrayOf(PropTypes.string),
  }),
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  showTitle: PropTypes.bool,
  message: PropTypes.string,
}

Confirmation.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
  showTitle: true,
  message: '',
}

export default Confirmation
