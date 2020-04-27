/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import googleIcon from '@assets/google-icon.png'
import linkedinIcon from '@assets/linkedin-icon.png'

import './stylesheets/SocialLoginButtons.scss'


export default function SocialLoginButtons(props){
  return (
    <div className="great-mvp-social-login-buttons">
      <a href={props.linkedinUrl} id="signup-modal-linkedin" className="great-mvp-wizard-step-button m-t-0 m-b-xs">
        <img src={linkedinIcon} />
        <span>Continue with LinkedIn</span>
      </a>
      <a href={props.googleUrl} id="signup-modal-google" className="great-mvp-wizard-step-button m-t-0 m-b-xs">
        <img src={googleIcon} />
        <span>Continue with Google</span>
      </a>
    </div>
  )
}


SocialLoginButtons.propTypes = {
  linkedinUrl: PropTypes.string.isRequired,
  googleUrl: PropTypes.string.isRequired,
}
