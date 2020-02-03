import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import ErrorList from './ErrorList'
import Services from './Services'


const styles = {
  close: {
    'float': 'right',
  },
  input: {
    width: '100%',
  },
  button: {
    background: '#000000',
    color: '#ffffff',
  },
  modal: {
    content: {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
      textAlign: 'center',
      width: 350,
      background: '#f5f2ed',
    }
  }
}


export default function LoginModal(props){
  const [errorMessage, setErrorMessage] = React.useState(props.errorMessage)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const usernameRef = React.createRef()
  const passwordRef = React.createRef()

  function handleSubmit(event){
    event.preventDefault()
    setErrorMessage('')
    setIsInProgress(true)
    Services.checkCredentials({
      url: props.loginUrl,
      username: usernameRef.current.value,
      password: passwordRef.current.value,
      csrfToken: props.csrfToken,
    }).then(response => {
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
      onRequestClose={props.handleClose}
      style={styles.modal}
      contentLabel='Login Modal'
    >
      <a href='#' className='link' onClick={handleClose} style={styles.close}>close</a>
      <h2 className='heading-large'>Login</h2>
      <form onSubmit={handleSubmit}>
        { errorMessage && <ErrorList message={errorMessage} /> }
        <div className='form-group'>
          <input
            type='text'
            placeholder='Email address'
            name='username'
            className='form-control'
            ref={usernameRef}
            disabled={isInProgress}
            style={styles.input}
          />
        </div>
        <div className='form-group'>
          <input
            type='password'
            placeholder='Password'
            name='password'
            className='form-control'
            ref={passwordRef}
            disabled={isInProgress}
            style={styles.input}
          />
        </div>
        <input
          type='submit'
          value='Log in'
          className='button'
          disabled={isInProgress}
          style={styles.button}
        />
      </form>
      <p>-- or --</p>
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
