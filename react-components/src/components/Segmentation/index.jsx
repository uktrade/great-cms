import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'

export default function Segmentation(props) {
  const { segment, handleModalClose } = props
  const [isOpen, setIsOpen] = useState(!segment)
  const [isInProgress, setIsInProgress] = useState()

  useEffect(() => {
    if (!isOpen) {
      handleModalClose()
    }
  }, [isOpen])

  const segmentQuestion = {
    name: 'segment',
    title: 'Which best describes you?',
    content: "We're asking our newest users one quick question to help us better understand their exporting experience."
  }

  const segmentAnswers = [
    {
      label: 'I have exported in the last 12 months',
      value: 'SUSTAIN',
    },
    {
      label: 'I have exported before but not in the last 12 months',
      value: 'REASSURE',
    },
    {
      label: 'I have never exported but have a product or service that is suitable or that could be developed for export',
      value: 'PROMOTE',
    },
    {
      label: 'I do not have a product or service for export',
      value: 'CHALLENGE',
    },
  ]

  const closeModal = () => {
    setIsOpen(false)
    handleModalClose()
  }

  const modalAfterOpen = () => {
    setIsInProgress(true)
  }

  const updateUserProfileSegment = (selection) => {
    Services.updateUserProfileSegment(selection.value)
      .then(() => {
        setIsInProgress(false)
      })
      .catch(() => {})
  }

  const content = () => {
    if (isInProgress)
      return (
        <Interaction
          question={segmentQuestion}
          answers={segmentAnswers}
          processResponse={updateUserProfileSegment}
        />
      )
    return (
      <div className="c-fullwidth">
        <h3 className="h-s">
          Thank you
        </h3>
        <p className="body-m m-b-xs text-blue-deep-60">
          Thank you for your response.
        </p>
        <button
          type="button"
          className="button button--primary m-t-xxs m-b-xs"
          disabled={false}
          onClick={closeModal}
          style={{ float: 'left', clear: 'both' }}
        >
          Close
        </button>
      </div>
    )
  }

  return (
    <ReactModal
      isOpen={isOpen}
      onRequestClose={handleModalClose}
      className="segmentation-modal modal p-v-xs p-h-s"
      overlayClassName="modal-overlay center"
      onAfterOpen={modalAfterOpen}
      shouldCloseOnOverlayClick={false}
    >
      {content()}
    </ReactModal>
  )
}

Segmentation.propTypes = {
  segment: PropTypes.string,
  handleModalClose: PropTypes.func,
}

Segmentation.defaultProps = {
  segment: '',
  handleModalClose: null,
}
