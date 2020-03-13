import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import { CookiesProvider } from 'react-cookie';
import { useCookies } from 'react-cookie';
import ReactModal from 'react-modal'

import Tour from './Tour'
import Modal from './Modal'


export function Base(props){
  const [cookies, setCookie] = useCookies([props.disableTourCookieName]); 

  const [isOpenModal, setIsOpenModal] = React.useState(cookies[props.disableTourCookieName] !== 'true')
  const [isOpenTour, setIsOpenTour] = React.useState()

  function handleSkipTour(error) {
    setIsOpenModal(false)
    setIsOpenTour(false)
    setCookie(props.disableTourCookieName, 'true');
  }

  function handleStartTour(nextStep) {
    setIsOpenModal(false)
    setIsOpenTour(true)
  }

  function handleTourClose() {
    setIsOpenTour(false)
    setCookie(props.disableTourCookieName, 'true');
  }

  return (
    <CookiesProvider>
      <Modal
        handleSkip={handleSkipTour}
        handleStart={handleStartTour}
        isOpen={isOpenModal}
        buttonText={props.buttonText}
        title={props.title}
        body={props.body}
      />
      <Tour
        isOpen={isOpenTour}
        handleClose={handleTourClose}
        steps={props.steps}
      />
    </CookiesProvider>
  )
}

Base.propTypes = {
  isOpen: PropTypes.bool,
}

Base.defaultProps = {
  isOpenTour: false,
  isOpenModal: false,

}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Base {...params} />, element)
}
