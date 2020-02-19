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
    textAlign: 'center',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    width: 430,
  },
  overlay: {
    zIndex: 1000,
  },
}

export function Modal(props){
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
    <div className='great-mvp-signup-modal'>
      <a
        id='header-sign-in-link'
        onClick={handleOpen}
        className='account-link signin'
        href='#'
      >Sign up</a>
      <ReactModal
        isOpen={isOpen}
        onRequestClose={handleClose}
        style={modalStyles}
        contentLabel="Modal"
      >
        <a
          href="#"
          className="link great-mvp-close"
          onClick={handleClose} >Close
        </a>
        <Wizard
          currentStep={props.currentStep}
          username={props.username}
          handleClose={handleClose}
        />
      </ReactModal>
    </div>
  )
}

Modal.propTypes = {
  isOpen: PropTypes.bool,
  currentStep: PropTypes.number,
  username: PropTypes.string,
}

Modal.defaultProps = {
  isOpen: false,
  username: '',
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Modal {...params} />, element)
}
