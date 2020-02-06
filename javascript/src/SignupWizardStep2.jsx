import React from 'react'
import PropTypes from 'prop-types'

import ErrorList from './components/ErrorList'
import Field from './components/Field'

const styles = {
  button: {
    background: '#333',
    color: '#ffffff',
    width: 300,
  },
  h2: {
    marginBottom: 35,
    marginTop: 25,
  },
  synopsis: {
    fontSize: 19,
    marginBottom: 30,
    marginTop: 0,
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



export default function SignupWizardStep2(props){
  return (
    <div>
      <h2 className="heading-xlarge" style={styles.h2}>Confirmation code</h2>
      <p className="body-text" style={styles.synopsis}>
        <span>we've emailed you a five-digit confirmation code.</span>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <ErrorList errors={props.errors} />
        <Field
          type="number"
          placeholder="Enter code"
          name="code"
          disabled={props.disabled}
          value={props.code}
          handleChange={props.handleCodeChange}
          autofocus={true}
        />
        <input
          type="submit"
          value="Submit"
          className="button"
          disabled={props.disabled}
          style={{...styles.button, ...styles.submit}}
        />
      </form>
    </div>
  )
}

SignupWizardStep2.propTypes = {
  code: PropTypes.string,
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleCodeChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
}

SignupWizardStep2.defaultProps = {
  code: '',
  disabled: false,
  errors: {},
}