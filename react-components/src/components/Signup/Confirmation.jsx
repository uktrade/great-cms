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
}) => (
  <form
    className="signup__confirmation"
    onSubmit={(event) => {
      event.preventDefault()
      handleSubmit()
    }}
  >
    <i class="fas fa-info-circle" aria-hidden="true"></i>

    {showTitle && (
      <legend className="h-s text-blue-deep-80 p-t-xs">Check your email</legend>
    )}
    <p className="m-b-s">
      We have emailed you a five-digit code. <br /> Enter it below:
    </p>
    <Input
      label="Confirmation code"
      id="code"
      placeholder="Enter code"
      disabled={disabled}
      value={code}
      onChange={(item) => handleCodeChange(item.code)}
      errors={errors.code || []}
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
}

Confirmation.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
  showTitle: true,
}

export default Confirmation
