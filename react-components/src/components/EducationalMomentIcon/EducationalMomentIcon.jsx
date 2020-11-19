import React from 'react'
import PropTypes from 'prop-types'

export default function EducationalMomentIcon(props) {
  const { ariaDescribedBy, hiddenText } = props

  return (
    <button type="button" className="educational-moment__button" aria-describedby={ariaDescribedBy}>
      <span className="visually-hidden">{hiddenText}</span>
      <i className="educational-moment__button-icon fas fa-book text-blue-deep-30" />
    </button>
  )
}

EducationalMomentIcon.propTypes = {
  ariaDescribedBy: PropTypes.string.isRequired,
  hiddenText: PropTypes.string.isRequired,
}
