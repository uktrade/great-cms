import React from 'react'
import PropTypes from 'prop-types'

const SocialLoginButtons = ({
  linkedinUrl,
  googleUrl,
  action
}) => {
  return (
    <>
      <a href={linkedinUrl} id="signup-modal-linkedin" title='Sign up with Linkedin' className="button button--secondary button--icon button--icon-left width-full m-b-xs">
        <i className="fab fa-linkedin" />
        <span>{action} with Linkedin</span>
      </a>
      <a href={googleUrl} id="signup-modal-google" title='Sign up with Google' className="button button--secondary button--icon button--icon-left width-full">
        <i className="fab fa-google" />
        <span>{action} with Google</span>
      </a>
    </>
  )
}

SocialLoginButtons.propTypes = {
  linkedinUrl: PropTypes.string.isRequired,
  googleUrl: PropTypes.string.isRequired,
  action: PropTypes.string,
}

SocialLoginButtons.defaultProps = {
  action: 'Continue'
}

export default SocialLoginButtons
