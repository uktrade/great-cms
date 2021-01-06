import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal'
import ProductFinderModal from '@src/components/ProductFinder/ProductFinderModal'

export const ProductNotSelected = memo(({ isOpen }) => {
  const [modal, setModal] = useState(isOpen)
  const [modalIsOpen, setIsOpen] = useState(false)

  const openProductFinder = () => {
    setIsOpen(true)
    setModal(false)
  }

  return (
    <>
      <ReactModal
        isOpen={modal}
        className="ReactModal__Content ReactModalCentreScreen"
        overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
        contentLabel="Modal"
      >
        <Modal
          backUrl="/export-plan/dashboard/"
          header="Add your product"
          content="You will need to choose a product before you can complete this section"
          onClick={openProductFinder}
          buttonText="Add a product"
          type="2"
        />
      </ReactModal>
      <ProductFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        setSelectedProduct={() => {}}
      />
    </>
  )
})

ProductNotSelected.propTypes = {
  isOpen: PropTypes.bool.isRequired,
}
