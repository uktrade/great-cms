import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'

export default function Questionnaire(props) {
  const { questions, answers, handleModalClose } = props
  const [isOpen, setIsOpen] = useState(true)
  const [isInProgress, setIsInProgress] = useState()

  useEffect(() => {
    if (!isOpen) {
      handleModalClose()
    }
  }, [isOpen])

  const segmentQuestion = questions[0]
  const segmentAnswers = segmentQuestion.choices

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

Questionnaire.propTypes = {
  segment: PropTypes.string,
  handleModalClose: PropTypes.func,
}

Questionnaire.defaultProps = {
  segment: '',
  handleModalClose: null,
}
