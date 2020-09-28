import React from 'react'
import PropTypes from 'prop-types'

export const FormGroup = ({
  children,
  error
}) => (
  <div
    className={`form-group ${error ? 'form-group-error' : ''}`}
  >
    {children}
  </div>
)

FormGroup.propTypes = {
  children: PropTypes.element.isRequired,
  error: PropTypes.bool
}

FormGroup.defaultProps = {
  error: false
}
