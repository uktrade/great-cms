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
    right: 'auto',
    textAlign: 'left',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    borderRadius: 10,
    padding: 0,
    width: 570,
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
    <div className="question-modal">
      <ReactModal
        isOpen={isOpen}
        onRequestClose={handleClose}
        style={modalStyles}
        contentLabel="Modal"
      >
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
}

Modal.defaultProps = {
  isOpen: false,
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Modal {...params} />, element)
}
