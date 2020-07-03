/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import Services from '@src/Services'

import '../../../../design-system/components/button/button'
import '../../../../design-system/components/link/link'

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
      <div className="great-mvp-tour-modal great-mvp-signup-wizard-step-1" id="page-tour-modal-step-1">
        <h2 className="great-mvp-tour-heading">{props.title}</h2>
        <p className="great-mvp-tour-text">{props.body}</p>
        <div className="great-mvp-tour-actions">
          <great-button
            id="page-tour-submit"
            theme="primary"
            size="large"
            onClick={(event) => {
              event.preventDefault()
              props.handleStart()
            }}
          >
            {props.buttonText}
          </great-button>
          <great-link
            id="page-tour-skip"
            theme="primary"
            href="#"
            onClick={(event) => {
              event.preventDefault()
              props.handleSkip()
            }}
          >
            Skip walk-through
          </great-link>
        </div>
      </div>
    </ReactModal>
  )
}

Modal.propTypes = {
  handleSkip: PropTypes.func.isRequired,
  handleStart: PropTypes.func.isRequired
}
