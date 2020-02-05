import React from 'react'
import PropTypes from 'prop-types'

import googleIcon from '../assets/google-icon.png'
import linkedinIcon from '../assets/linkedin-icon.png'


const styles = {
  img: {
    verticalAlign: 'middle',
  },
  span: {
    verticalAlign: 'middle',
    marginLeft: 10,
    display: 'inline-block',
  },
  a: {
    background: '#333',
    color: '#ffffff',
    width: 300,
  },
  linkedin: {
    marginBottom: 20,
  },
}

export default function SocialLoginButtons(props){
  return (
    <div>
      <a href={props.linkedInUrl} className="button" style={{...styles.a, ...styles.linkedin}}>
        <img style={styles.img} src={linkedinIcon} />
        <span style={styles.span}>Continue with LinkedIn</span>
      </a>
      <a href={props.googleUrl} className="button" style={styles.a}>
        <img style={styles.img} src={googleIcon} />
        <span style={styles.span}>Continue with Google</span>
      </a>
    </div>
  )
}
  

SocialLoginButtons.propTypes = {
  linkedInUrl: PropTypes.string.isRequired,
  googleUrl: PropTypes.string.isRequired,
}
