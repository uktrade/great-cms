import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Wizard from './Wizard'

import './stylesheets/Modal.scss'


const modalStyles = {
  content : {
    background: '#f5f2ed',
    bottom: 'auto',
    left: '50%',
    marginRight: '-50%',
    padding: 30,
    right: 'auto',
    top: '50%',
    top: 75,
    width: 430,
    inset: '75px auto auto 17%',
    height: '100%',
  },
  overlay: {
    zIndex: 1000,
    backgroundColor: 'transparent',
  },
}


export default function Modal(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen)

  function handleOpen(event) {
    event.preventDefault()
    setIsOpen(true)
  }

  function handleClose(event){
    event.preventDefault()
    setIsOpen(false)
  }

  function getCloseButton() {
    if (props.preventClose) {
      return <div className="m-t-l">&nbsp;</div>
    } else {
      return (
        <a
          href="#"
          className="link great-mvp-close"
          onClick={handleClose} >Close
        </a>
      )
    }
  }

  return (
    <div className='great-mvp-signup-modal'>
      <a
        id='header-sign-in-link'
        onClick={handleOpen}
        className='account-link signin'
        href='#'
      >Sign up</a>
      <ReactModal
        isOpen={isOpen}
        onRequestClose={!props.preventClose && handleClose}
        style={modalStyles}
        contentLabel="Modal"
        id="signup-modal"
      >
        {getCloseButton()}
        <Wizard
          currentStep={props.currentStep}
          username={props.username}
          handleClose={handleClose}
          nextUrl={props.nextUrl}
          showCredentialsLede={true}
        />
      </ReactModal>
    </div>
  )
}

Modal.propTypes = {
  isOpen: PropTypes.bool,
  currentStep: PropTypes.number,
  username: PropTypes.string,
  nextUrl: PropTypes.string.isRequired,
  preventClose: PropTypes.bool,
}

Modal.defaultProps = {
  isOpen: false,
  username: '',
  preventClose: false,
}
