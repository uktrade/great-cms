import React from 'react'
import PropTypes from 'prop-types'

export const Complete = ({
   showTitle,
   nextUrl
 }) => (
  <div id='signup-modal-success'>
    <i className='fas fa-check-circle text-green-100 icon-large' />
    {showTitle && <h2 className='h-s text-blue-deep-80'>Sign up complete</h2>}
    <p className='body-l text-black-100'>Your account has been created.</p>
    <a
      id='signup-modal-submit-success'
      className='button button--primary'
      href={nextUrl}
    >Continue to the dashboard</a>
  </div>
)


Complete.propTypes = {
  nextUrl: PropTypes.string.isRequired,
  showTitle: PropTypes.bool,
}

Complete.defaultProps = {
  showTitle: true,
}
