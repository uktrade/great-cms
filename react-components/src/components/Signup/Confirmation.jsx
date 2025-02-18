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

    {showTitle && (
      <legend className="govuk-padding-top-3 govuk-!-margin-top-7 "><h1 className='govuk-heading-m great-line-height-40'>Check your email</h1></legend>
    )}
    <p className="govuk-margin-bottom-2">
    We&#39;ve sent a code to your email address. Don&#39;t forget to check your spam folder if you can&#39;t see it. <br /> Enter the code below to complete registration:
    </p>
    <Input
      label="Confirmation code"
      id="code"
      disabled={disabled}
      value={code}
      onChange={(item) => handleCodeChange(item.code)}
      errors={errors.code || []}
      message={message}
    />
    <button
      type="submit"
      id="signup-modal-submit-code"
      className="button primary-button govuk-margin-top-0 great-border-bottom-black great-width-auto"
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
