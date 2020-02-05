import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import ErrorList from './ErrorList'
import Field from './Field'
import SocialLoginButtons from './SocialLoginButtons'
import Services from './Services'
import VerticalSeparator from './VerticalSeparator'

const styles = {
  close: {
    width: '100%',
    fontSize: 20,
    display: 'inline-block',
    textAlign: 'right',
  },
  button: {
    background: '#333',
    color: '#ffffff',
    width: 300,
  },
  synopsis: {
    fontSize: 20,
    marginBottom: 30,
  },
  heading: {
    marginBottom: 0,
  },
  terms: {
    fontSize: 20,
    marginBottom: 60,
  },
  modal: {
    content : {
      background: '#f5f2ed',
      bottom: 'auto',
      left: '50%',
      marginRight: '-50%',
      padding: 35,
      right: 'auto',
      textAlign: 'center',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      width: 450,
    },
    overlay: {
      zIndex: 1000,
    },
  }
}


export default function SignupModal(props){
  const [errorMessage, setErrorMessage] = React.useState(props.errorMessage)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [username, setUsername] = React.useState('')
  const [password, setPassword] = React.useState('')

  function handleSubmit(event){
    event.preventDefault()
    setErrorMessage('')
    setIsInProgress(true)
    const data = { url: props.signupUrl, username, password, csrfToken: props.csrfToken}
    Services.createUser(data)
      .then(response => {
        location.reload()
      })
      .catch(error => {
        const message = error.message || error
        setErrorMessage(error)
        setIsInProgress(false)
      })
  }

  function handleClose(event) {
    event.preventDefault()
    props.handleClose();
  }

  return (
    <Modal
      isOpen={props.isOpen}
      onRequestClose={props.handleClose}
      style={styles.modal}
      contentLabel="Login Modal"
    >
      <a href="#" className="link" onClick={handleClose} style={styles.close}>Close</a>
      <h2 className="heading-xlarge" style={styles.heading}>Sign up</h2>
      <p className="body-text" style={styles.synopsis}>
        <span>It's easier to sign up now and save your progress, already have an account? </span>
        <a href="#" onClick={props.handleLoginOpen}>Log in</a>
      </p>
      <SocialLoginButtons linkedInUrl={props.linkedInUrl} googleUrl={props.googleUrl} />
      <VerticalSeparator />
      <form onSubmit={handleSubmit}>
        { errorMessage && <ErrorList message={errorMessage} /> }
        <Field
          type="text"
          placeholder="Email address"
          name="username"
          disabled={isInProgress}
          value={username}
          handleChange={setUsername}
        />
        <Field
          type="password"
          placeholder="Password"
          name="password"
          disabled={isInProgress}
          value={password}
          handleChange={setPassword}
        />
        <p style={styles.terms}>By clicking Sign up, you accept the <a href={props.termsUrl} target="_blank">terms and conditions</a> of the great.gov.uk service.</p>
        <input
          type="submit"
          value="Sign up"
          className="button"
          disabled={isInProgress}
          style={styles.button}
        />
      </form>
    </Modal>
  )
}

SignupModal.propTypes = {
  csrfToken: PropTypes.string.isRequired,
  errorMessage: PropTypes.string,
  googleUrl: PropTypes.string.isRequired,
  handleClose: PropTypes.func.isRequired,
  handleLoginOpen: PropTypes.func.isRequired,
  isInProgress: PropTypes.bool,
  isOpen: PropTypes.bool,
  linkedInUrl: PropTypes.string.isRequired,
  signupUrl: PropTypes.string.isRequired,
  termsUrl: PropTypes.string.isRequired,
}

SignupModal.defaultProps = {
  isOpen: false,
  errorMessage: '',
  isInProgress: false,
}