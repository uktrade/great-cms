import React from 'react'
import PropTypes from 'prop-types'

const Complete = ({
   showTitle,
   nextUrl
 }) => (
  <div id='signup__complete'>
    <span role='img' className='fas fa-check-circle text-green-100 icon-large' />
    {showTitle && <h1 className='h-s'>Sign up complete</h1>}
    <p className='body-l text-black-100'>Your account has been created.</p>
    <a
      id='signup-modal-submit-success'
      className='button primary-button great-border-bottom-black great-width-auto'
      href={nextUrl}
    >Continue</a>
  </div>
)

export default Complete


Complete.propTypes = {
  nextUrl: PropTypes.string.isRequired,
  showTitle: PropTypes.bool,
}

Complete.defaultProps = {
  showTitle: true,
}
