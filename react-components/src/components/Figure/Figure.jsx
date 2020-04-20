import React from 'react'
import PropTypes from 'prop-types'
import './Figure.scss'

export default function Figure(props) {
  const { image, caption } = props
  return (
    <figure className="figure">
      <div className="figure__image-wrapper">
        <img className="figure__image" src={image} alt="" />
      </div>
      <figcaption className="figure__caption">{caption}</figcaption>
    </figure>
  )
}

Figure.propTypes = {
  image: PropTypes.string.isRequired,
  caption: PropTypes.string.isRequired,
}
