import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'
import { mapArray } from '@src/Helpers'

export default function Questionnaire(props) {
  const { handleModalClose } = props
  const [showClose, setShowClose] = useState()
  const [question, setQuestion] = useState()
  const [questions, setQuestions] = useState()

  const setNextQuestion = (questionnaire) => {
    // work out last answered question (may be better in BE)
    if (questionnaire && questionnaire.questions) {
      const sorted = questionnaire.questions.sort((q1, q2) => {
        return q1.order > q2.order ? 1 : -1
      })
      setQuestions(sorted)
      const answers = mapArray(questionnaire.answers, 'question_id')
      const firstUnansweredQuestion = sorted.reduce((out, question) => {
        const answered = answers[question.id]
        if (answered) {
          question['answer'] = answered.answer
        }
        return out || (!answered && question)
      }, null)
      if (question) {
        // follwing saving an answer
        const index = questions.findIndex((q) => q.id == question.id)
        setQuestion(questions[index + 1])
      } else {
        // initial
        setQuestion(firstUnansweredQuestion)
        if (!firstUnansweredQuestion) {
          closeModal()
        }
      }
    }
  }

  useEffect(() => {
    Services.getUserQuestionnaire().then((questionnaire) => {
      setNextQuestion(questionnaire)
    })
  }, [])

  const closeModal = () => {
    setShowClose(false)
    handleModalClose()
  }

  const goBack = () => {
    const index = questions.findIndex((q) => q.id == question.id)
    setQuestion(questions[index - 1])
  }

  const modalAfterOpen = () => {}

  const setQuestionAnswer = (selection) => {
    Services.setUserQuestionnaireAnswer(question.id, selection.value)
      .then((questionnaire) => {
        if (!questionnaire || !questionnaire.answers) {
          setShowClose(true)
          setQuestion(null)
        }
        setNextQuestion(questionnaire)
      })
      .catch(() => {})
  }

  const content = () => {
    if (question)
      return (
        <Interaction
          question={question}
          answers={question.choices}
          initialSelection={question.answer}
          processResponse={setQuestionAnswer}
          goBack={goBack}
        />
      )
    if (showClose)
      return (
        <div className="c-fullwidth">
          <h3 className="h-s">Thank you</h3>
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
      isOpen={!!(question || showClose)}
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
