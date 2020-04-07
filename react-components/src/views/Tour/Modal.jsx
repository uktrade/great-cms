/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import Services from '@src/Services'


import './stylesheets/Tour.scss'


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
    width: 490,
  },
  overlay: {
    zIndex: 1000,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
}


export default function Modal(props){

  return (
    <ReactModal
      isOpen={props.isOpen}
      style={modalStyles}
      onRequestClose={props.handleSkip}
      contentLabel="Modal"
    >
      <div className="great-mvp-signup-wizard-step-1 p-s" id="page-tour-modal-step-1">
        <h2 className="h-m">{props.title}</h2>
        <p>{props.body}</p>
        <input
          type="submit"
          value={props.buttonText}
          className="great-mvp-tour-button p-v-xxs p-h-xs"
          id="page-tour-submit"
          onClick={event => { event.preventDefault(); props.handleStart()}}
        />
          <p className="m-t-xxs">
            <a
              href="#"
              id="page-tour-skip"
              onClick={event => { event.preventDefault(); props.handleSkip()}}
            >Skip walk-through</a>
          </p>
      </div>
    </ReactModal>
  )
 
}

Modal.propTypes = {
  handleSkip: PropTypes.func.isRequired,
  handleStart: PropTypes.func.isRequired,
}
