import React from 'react'
import PropTypes from 'prop-types'
import OpenBookIcon from '@assets/open-book-icon.png'

export default function EducationalMomentIcon(props) {
  const { ariaDescribedBy, hiddenText } = props

  return (
      <button type="button" className="educational-moment__button" aria-describedby={ariaDescribedBy}>
          <span className="visually-hidden">{hiddenText}</span>
          <img className="educational-moment__button-image" src={OpenBookIcon} alt="" />
      </button>
  )

}

EducationalMomentIcon.propTypes = {
  ariaDescribedBy: PropTypes.string.isRequired,
  hiddenText: PropTypes.string.isRequired,
}
