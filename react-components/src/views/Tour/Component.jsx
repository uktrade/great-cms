/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import { CookiesProvider } from 'react-cookie'

import Tour from './Tour'
import Modal from './Modal'

export default function Component(props) {
  return (
    <CookiesProvider>
      <Modal
        handleSkip={props.handleSkip}
        handleStart={props.handleStart}
        handleDisable={props.handleDisable}
        isOpen={props.isOpenModal}
        buttonText={props.buttonText}
        title={props.title}
        body={props.body}
      />
      <Tour isOpen={props.isOpenTour} handleClose={props.handleTourClose} steps={props.steps} />
    </CookiesProvider>
  )
}

Component.propTypes = {
  body: PropTypes.string.isRequired,
  buttonText: PropTypes.string.isRequired,
  handleSkipTour: PropTypes.func.isRequired,
  handleStartTour: PropTypes.func.isRequired,
  handleTourClose: PropTypes.func.isRequired,
  handleDisable: PropTypes.func.isRequired,
  isOpen: PropTypes.bool,
  isOpenModal: PropTypes.bool,
  isOpenTour: PropTypes.bool,
  steps: PropTypes.array.isRequired,
  title: PropTypes.string.isRequired
}

Component.defaultProps = {
  isOpenTour: false,
  isOpenModal: false
}
