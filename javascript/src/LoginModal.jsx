import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import ErrorList from './ErrorList'
import Field from './Field'
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
  },
  modal: {
    content: {
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


export default function LoginModal(props){
  const [errorMessage, setErrorMessage] = React.useState(props.errorMessage)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [username, setUsername] = React.useState('')
  const [password, setPassword] = React.useState('')

  function handleSubmit(event){
    event.preventDefault()
    setErrorMessage('')
    setIsInProgress(true)
    const data = {url: props.loginUrl, username, password, csrfToken: props.csrfToken}
    Services.checkCredentials(data)
      .then(response => {
        location.reload()
      })
      .catch(error => {
        const message = error.message || error
        setErrorMessage(message)
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
      parentSelector={() => document.body}
      onRequestClose={props.handleClose}
      style={styles.modal}
      contentLabel='Login Modal'
    >
      <a href='#' className='link' onClick={handleClose} style={styles.close}>Close</a>
      <h2 className='heading-xlarge'>Login</h2>
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
        <input
          type='submit'
          value='Log in'
          className='button'
          disabled={isInProgress}
          style={styles.button}
        />
      </form>
      <VerticalSeparator />
      <a onClick={props.handleSignupClick} className='button' style={styles.button}>Signup</a>
    </Modal>
  )
}

LoginModal.propTypes = {
  isOpen: PropTypes.bool,
  handleClose: PropTypes.func.isRequired,
  errorMessage: PropTypes.string,
  isInProgress: PropTypes.bool,
  loginUrl: PropTypes.string.isRequired,
  csrfToken: PropTypes.string.isRequired,
  handleSignupClick: PropTypes.func.isRequired,
}

LoginModal.defaultProps = {
  isOpen: false,
  errorMessage: '',
  isInProgress: false,
}
