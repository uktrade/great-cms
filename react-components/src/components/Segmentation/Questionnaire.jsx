import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'
import { mapArray } from '@src/Helpers'

export default function Questionnaire(props) {
  const modes = {closed: 'c', start:'s', question:'q', thankyou:'t' }
  const { handleModalClose } = props
  const [mode, setMode] = useState(modes.closed)
  const [question, _setQuestion] = useState()
  const [questions, setQuestions] = useState()
  const [value, setValue] = useState()



  const questionIndex = () => {
    return questions && question && (questions.findIndex((q) => q.id == question.id))
  }

  const setQuestion = (question) => {
    if (question && mode == modes.closed) setMode(modes.start)
    setValue((question && question.answer) || null)
    _setQuestion(question)
  }

  const setNextQuestion = (questionnaire) => {
    // Work out last answered question (may be better in BE)
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
        setQuestion(questions[questionIndex() + 1])
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
      if (questionnaire) {
        setNextQuestion(questionnaire)
      }
    })
  }, [])

  const closeModal = () => {
    setMode(modes.closed)
    handleModalClose()
  }

  const goBack = () => {
    setQuestion(questions[questionIndex() - 1])
  }

  const modalAfterOpen = () => {}

  const setQuestionAnswer = () => {
    Services.setUserQuestionnaireAnswer(question.id, value)
      .then((questionnaire) => {
        if (!questionnaire || !questionnaire.answers) {
          setMode(modes.thankyou)
          setQuestion(null)
        }
        setNextQuestion(questionnaire)
      })
      .catch(() => {})
  }

  const progress =
    question && questions && `${100 * (questionIndex() / questions.length)}%`
  const content = () => {
    if (mode == modes.start)
      return (
        <div className="c-fullwidth body-l text-blue-deep-60">
          {!questionIndex() ? (
            <>
              <h3 className="h-s">Help us serve you better</h3>
              <p className="m-v-xs">
                We’re surveying exporters on Great.gov.uk to better understand
                their exporting experience and needs. This will help the
                Department to better support exporters across the country.
              </p>
              <p className="m-v-xs">
                It will take about 3-5 minutes to complete.
              </p>
            </>
          ) : (
            <>
              <h3 className="h-s">You started but didn't finish</h3>
              <p className="m-v-xs">
                You left the survey partly completed. It would be a great help to us if you
                could complete the survey now.
              </p>
              <p className="m-v-xs">
                It will take about 3-5 minutes to complete.
              </p>
            </>
          )}
          <button
            type="button"
            className="button button--tertiary m-t-xxs m-b-xs"
            disabled={false}
            onClick={closeModal}
            style={{ float: 'left', clear: 'both' }}
          >
            Not now
          </button>
          <button
            type="button"
            className="button button--primary m-t-xxs m-b-xs"
            disabled={false}
            onClick={() => setMode(modes.question)}
            style={{ float: 'right' }}
          >
            Continue
          </button>
        </div>
      )
    if (mode == modes.question)
      return (
        <>
          <Interaction question={question} value={value} setValue={setValue} />
          <div
            style={{
              display: 'flex',
              flexFlow: 'row nowrap',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: '4 0' }}>
              <div className="progress-bar m-r-m">
                <span style={{ width: progress }}></span>
              </div>
            </div>
            {questionIndex() > 0 ? (
              <button
                type="button"
                className="button button--tertiary m-v-xs m-f-xxs"
                onClick={goBack}
              >
                Back
              </button>
            ) : (
              ''
            )}
            <button
              type="button"
              className="button button--primary m-v-xs m-f-xxs"
              disabled={!value}
              onClick={setQuestionAnswer}
            >
              Next
            </button>
          </div>
        </>
      )
    if (mode == modes.thankyou)
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
      isOpen={mode != modes.closed}
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
