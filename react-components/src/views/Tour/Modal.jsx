/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import Services from '@src/Services'

import './stylesheets/Tour.scss'

const modalStyles = {
  content: {
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
    width: 490
  },
  overlay: {
    zIndex: 1000,
    backgroundColor: 'rgba(0, 0, 0, 0.5)'
  }
}

export default function Modal(props) {
  return (
    <ReactModal isOpen={props.isOpen} style={modalStyles} onRequestClose={props.handleSkip} contentLabel="Modal">
      <div className="great-tour-modal great-signup-wizard-step-1" id="page-tour-modal-step-1">
        <img src="/static/images/learning-modal.png" alt="" />
        <h2 className="great-tour-heading m-t-s">{props.title}</h2>
        <p className="great-tour-text">{props.body}</p>
        <div className="great-tour-actions">
          <button
            id="page-tour-submit"
            className="button button--primary button--large"
            onClick={(event) => {
              event.preventDefault()
              props.handleStart()
            }}
          >
            {props.buttonText}
          </button>
          <a
            id="page-tour-skip"
            className="link"
            href="#"
            onClick={(event) => {
              event.preventDefault()
              props.handleSkip()
            }}
          >
            Skip walk-through
          </a>
        </div>
      </div>
    </ReactModal>
  )
}

Modal.propTypes = {
  handleSkip: PropTypes.func.isRequired,
  handleStart: PropTypes.func.isRequired
}
