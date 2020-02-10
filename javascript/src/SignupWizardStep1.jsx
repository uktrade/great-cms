import React from 'react'
import PropTypes from 'prop-types'

import Services from './Services'
import ErrorList from './components/ErrorList'
import Field from './components/Field'
import SocialLoginButtons from './components/SocialLoginButtons'
import VerticalSeparator from './components/VerticalSeparator'

const styles = {
  button: {
    background: '#333',
    color: '#ffffff',
    width: 300,
  },
  h2: {
    marginBottom: 0,
    marginTop: 25,
    marginBottom: 35,
  },
  synopsis: {
    marginTop: 0,
    fontSize: 19,
    marginBottom: 30,
  },
  terms: {
    fontSize: 19,
    marginBottom: 50,
    marginTop: 10, // complements 30px margin of the form-group above it
  },
  submit: {
    marginBottom: 15, // complements 30px padding of the modal
    height: 41,
  },
}


export default function SignupWizardStep1(props){
  return (
    <div>
      <h2 className="heading-xlarge" style={styles.h2}>Sign up</h2>
      <p className="body-text" style={styles.synopsis}>
        <span>It's easier to sign up now and save your progress, already have an account? </span>
        <a href="#">Log in</a>
      </p>
      <SocialLoginButtons />
      <VerticalSeparator />
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <ErrorList errors={props.errors} />
        <Field
          type="text"
          placeholder="Email address"
          name="username"
          disabled={props.disabled}
          value={props.username}
          handleChange={props.handleUsernameChange}
          autofocus={true}
        />
        <Field
          type="password"
          placeholder="Password"
          name="password"
          disabled={props.disabled}
          value={props.password}
          handleChange={props.handlePasswordChange}
        />
        <p style={styles.terms}>By clicking Sign up, you accept the <a href={Services.config.termsUrl} target="_blank">terms and conditions</a> of the great.gov.uk service.</p>
        <input
          type="submit"
          value="Sign up"
          className="button"
          disabled={props.disabled}
          style={{...styles.button, ...styles.submit}}
        />
      </form>
    </div>
  )
}

SignupWizardStep1.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handlePasswordChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleUsernameChange: PropTypes.func.isRequired,
  password: PropTypes.string,
  username: PropTypes.string,
}

SignupWizardStep1.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  username: '',
}