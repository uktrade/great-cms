import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ isOpen, onClick }) => (
  <ReactModal
    isOpen={isOpen}
    className="ReactModal__Content ReactModalCentreScreen"
    overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
    contentLabel="Modal"
  >
    <Modal
      backUrl="/export-plan/dashboard/"
      header="Some sections aren’t available yet"
      content="This Beta version is limited"
      onClick={onClick}
      buttonText="Ok"
      type={3}
    />
  </ReactModal>
)

ComingSoon.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired
}
