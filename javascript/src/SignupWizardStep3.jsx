import React from 'react'
import PropTypes from 'prop-types'


const styles = {
  h2: {
    marginBottom: 0,
    marginTop: 25,
  },
  synopsis: {
    fontSize: 19,
    marginBottom: 30,
    marginBottom: 30,
    paddingTop: 45,
    textAlign: 'left',
  },
  subtitle: {
    fontSize: 19,
    marginTop: 10,
    marginBottom: 0,
  },
  submit: {
    marginBottom: 15, // complements 30px padding of the modal
    height: 41,
    fontSize: 19,
    cursor: 'pointer',
  },
}



export default function SignupWizardStep3(props){
  return (
    <div>
      <h2 className="heading-xlarge" style={styles.h2}>Complete</h2>
      <p style={styles.subtitle}>Your account has been created.</p>
      <p className="body-text" style={styles.synopsis}>
        <p>You can now:</p>
        <ul className="list list-bullet">
          <li>Start using your Great.gov.uk Dashboard</li>
          <li>Create an export plan</li>
          <li>Save your progress in learning</li>
        </ul>
      </p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <input
          type="submit"
          value="Continue"
          className="link"
          disabled={props.disabled}
          style={{...styles.submit}}
        />
      </form>
    </div>
  )
}


SignupWizardStep3.PropTypes = {
  handleSubmit: PropTypes.func.isRequired,
}
