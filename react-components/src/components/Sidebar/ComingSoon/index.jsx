import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ isOpen, onClick }) => (
  <ReactModal
    isOpen={isOpen}
    className='ReactModal__Content ReactModalCentreScreen'
    overlayClassName='ReactModal__Overlay ReactModalCentreScreen'
    contentLabel='Modal'
  >
    <Modal
      backUrl='/export-plan/dashboard/'
      header='This feature is coming soon'
      content='This feature is not available in Beta version of the new great.gov.uk platform.'
      onClick={onClick}
      buttonText='Ok'
    />
  </ReactModal>
)

ComingSoon.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired
}
