/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import { useCookies } from 'react-cookie'
import ReactModal from 'react-modal'

import Component from './Component'

export function Container(props) {
  const [cookies, setCookie] = useCookies([props.disableTourCookieName])
  const [isOpenModal, setIsOpenModal] = React.useState(cookies[props.disableTourCookieName] !== 'true')
  const [isOpenTour, setIsOpenTour] = React.useState()

  function handleSkipTour(error) {
    setIsOpenModal(false)
    setIsOpenTour(false)
  }

  function handleStartTour(nextStep) {
    setIsOpenModal(false)
    setIsOpenTour(true)
  }

  function handleTourClose() {
    setIsOpenTour(false)
  }

  function handleTourDisable() {
    setCookie(props.disableTourCookieName, 'true')
    setIsOpenModal(false)
    setIsOpenTour(false)
  }

  return (
    <Component
      handleSkip={handleSkipTour}
      handleStart={handleStartTour}
      handleDisable={handleTourDisable}
      isOpenModal={isOpenModal}
      buttonText={props.buttonText}
      title={props.title}
      body={props.body}
      isOpenTour={isOpenTour}
      handleTourClose={handleTourClose}
      steps={props.steps}
    />
  )
}

Container.propTypes = {
  isOpen: PropTypes.bool
}

Container.defaultProps = {
  isOpenTour: false,
  isOpenModal: false
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Container {...params} />, element)
}
