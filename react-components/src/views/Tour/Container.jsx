/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie'
import Component from './Component'

export default function Container(props) {
  const { tour, disableTourCookieName, handleModalClose } = props
  const [cookies, setCookie] = useCookies([disableTourCookieName])
  const [isOpenModal, setIsOpenModal] = React.useState(cookies[disableTourCookieName] !== 'true')
  const [isOpenTour, setIsOpenTour] = React.useState()

  const handleSkipTour = () => {
    setIsOpenModal(false)
    setIsOpenTour(false)
    handleModalClose()
  }

  const handleStartTour = (nextStep) => {
    setIsOpenModal(false)
    setIsOpenTour(true)
  }

  const handleTourClose = () => {
    setIsOpenModal(false)
    setIsOpenTour(false)
    handleModalClose()
  }

  const handleTourDisable = () => {
    setCookie(disableTourCookieName, 'true')
    setIsOpenModal(false)
    setIsOpenTour(false)
    handleModalClose()
  }

  return (
    <Component
      handleSkip={handleSkipTour}
      handleStart={handleStartTour}
      handleDisable={handleTourDisable}
      isOpenModal={isOpenModal}
      buttonText={tour.button_text}
      title={tour.title}
      body={tour.body}
      isOpenTour={isOpenTour}
      handleTourClose={handleTourClose}
      steps={tour.steps}
    />
  )
}

Container.propTypes = {
  tour: PropTypes.shape({
    title: PropTypes.string,
    button_text: PropTypes.string,
    body: PropTypes.string,
    steps: PropTypes.array,
  }),
  disableTourCookieName: PropTypes.string.isRequired,
  handleModalClose: PropTypes.func,
}

Container.defaultProps = {
  isOpenTour: false,
  isOpenModal: false
}
