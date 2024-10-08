import React from 'react'
import PropTypes from 'prop-types'

export default function ErrorList(props){
  if (props.errors.length === 0) {
    return null
  }

  return (
    <ul className={`great-mvp-error-list errorlist ${props.className}`}>
      {props.errors.map((error, i) => <li key={i} className="govuk-error-message">{error}</li> )}
    </ul>
  )
}


ErrorList.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string).isRequired,
  className: PropTypes.string,
}

ErrorList.defaultProps = {
  className: ''
}
