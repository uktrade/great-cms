import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import SignupWizard from './SignupWizard'


const styles = {
  close: {
    width: '100%',
    fontSize: 19,
    display: 'inline-block',
    textAlign: 'right',
  },
  modal: {
    content : {
      background: '#f5f2ed',
      bottom: 'auto',
      left: '50%',
      marginRight: '-50%',
      padding: 30,
      right: 'auto',
      textAlign: 'center',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      width: 430,
    },
    overlay: {
      zIndex: 1000,
    },
  }
}

export function SignupModal(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen)

  function handleOpen(event) {
    event.preventDefault()
    setIsOpen(true)
  }

  function handleClose(event){
    event.preventDefault()
    setIsOpen(false)
  }

  return (
    <div>
      <a
        id='header-sign-in-link'
        onClick={handleOpen}
        className='account-link signin'
        href='#'
      >Sign up</a>
      <Modal
        isOpen={isOpen}
        onRequestClose={handleClose}
        style={styles.modal}
        contentLabel="Modal"
      >
        <a
          href="#"
          className="link"
          onClick={handleClose}
          style={styles.close}>Close
        </a>
        <SignupWizard
          currentStep={props.currentStep}
          username={props.username}
          handleClose={handleClose}
        />
      </Modal>
    </div>
  )
}

SignupModal.propTypes = {
  isOpen: PropTypes.bool,
  currentStep: PropTypes.number,
  username: PropTypes.string,
}

SignupModal.defaultProps = {
  isOpen: false,
  username: '',
}

export default function createSignupModal({ element, ...params }) {
  Modal.setAppElement(element)
  ReactDOM.render(<SignupModal {...params} />, element)
}
