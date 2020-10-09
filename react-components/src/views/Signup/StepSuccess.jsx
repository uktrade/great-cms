import React from 'react'
import PropTypes from 'prop-types'

const StepSuccess = ({
  showTitle,
  nextUrl
}) => {
  return (
    <div id="signup-modal-success">
      <i className="fas fa-check-circle" />
      {showTitle && <h2 className="h-m text-blue-deep-80 body-l">Sign up complete</h2>}
      <p>Your account has been created.</p>
      <a
        id="signup-modal-submit-success"
        className="button button--primary"
        href={nextUrl}
      >Continue to the dashboard</a>
    </div>
  )
}

StepSuccess.propTypes = {
  nextUrl: PropTypes.string.isRequired,
  showTitle: PropTypes.bool,
}

StepSuccess.defaultProps = {
  showTitle: true,
}

export default StepSuccess
