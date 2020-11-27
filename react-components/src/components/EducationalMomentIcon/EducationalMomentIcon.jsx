import React, { memo } from 'react'
import PropTypes from 'prop-types'

const EducationalMomentIcon = memo(({
  ariaDescribedBy,
  hiddenText
}) => (
  <button type='button' className='button button--small button--only-icon button--tertiary' aria-describedby={ariaDescribedBy}>
    <i className='fas fa-book'><span className="visually-hidden">{hiddenText}</span></i>
  </button>
))

EducationalMomentIcon.propTypes = {
  ariaDescribedBy: PropTypes.string.isRequired,
  hiddenText: PropTypes.string.isRequired,
}

export default EducationalMomentIcon
