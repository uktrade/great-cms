import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import { CookiesProvider } from 'react-cookie';
import { useCookies } from 'react-cookie';
import ReactModal from 'react-modal'

import Tour from './Tour'
import Modal from './Modal'


export function Base(props){
  const [cookies, setCookie] = useCookies(['disable_tour']); 

  const [isOpenModal, setIsOpenModal] = React.useState(cookies.disable_tour !== 'true')
  const [isOpenTour, setIsOpenTour] = React.useState()

  function handleSkipTour(error) {
    setIsOpenModal(false)
    setIsOpenTour(false)
    setCookie('disable_tour', 'true');
  }

  function handleStartTour(nextStep) {
    setIsOpenModal(false)
    setIsOpenTour(true)
  }

  function handleTourClose() {
    setIsOpenTour(false)
    setCookie('disable_tour', 'true');
  }

  return (
    <CookiesProvider>
      <Modal
        handleSkip={handleSkipTour}
        handleStart={handleStartTour}
        isOpen={isOpenModal}
      />
      <Tour
        isOpen={isOpenTour}
        handleClose={handleTourClose}
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
