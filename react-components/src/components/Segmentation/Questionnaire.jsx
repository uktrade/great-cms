import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { mapArray } from '@src/Helpers'
import Interaction from './Interaction'
import Modal from './Modal'

export default function Questionnaire(props) {
  const modes = { closed: 'c', start: 's', question: 'q', thankyou: 't' }
  const { handleModalClose } = props
  const [mode, setMode] = useState(modes.closed)
  const [question, _setQuestion] = useState()
  const [questions, setQuestions] = useState()
  const [value, setValue] = useState()

  const closeModal = () => {
    setMode(modes.closed)
    handleModalClose()
  }

  const questionIndex = () => {
    return (
      questions && question && questions.findIndex((q) => q.id === question.id)
    )
  }

  const setQuestion = (newQuestion) => {
    if (newQuestion && mode === modes.closed) setMode(modes.start)
    setValue((newQuestion && newQuestion.answer) || null)
    _setQuestion(newQuestion)
  }

  const setNextQuestion = (questionnaire) => {
    // Work out last answered question (may be better in BE)
    if (questionnaire && questionnaire.questions) {
      const sorted = questionnaire.questions.sort((q1, q2) => {
        return q1.order > q2.order ? 1 : -1
      })
      setQuestions(sorted)
      const answers = mapArray(questionnaire.answers, 'question_id')
      const firstUnansweredQuestion = sorted.reduce((out, loopQuestion) => {
        const answered = answers[loopQuestion.id]
        if (answered) {
          loopQuestion.answer = answered.answer
        }
        return out || (!answered && loopQuestion)
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

  const goBack = () => {
    const newQuestion = questions[questionIndex() - 1]
    if (!newQuestion) {
      setMode(modes.start)
    } else {
      setQuestion(newQuestion)
    }
  }

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

  if (mode === modes.start)
    return (
      <Modal
        className="segmentation-modal"
        title={
          questionIndex() ? 'Survey in progress' : 'Help us serve you better'
        }
        body={
          <>
            {!questionIndex() ? (
              <p className="m-v-xs">
                We&#39;re surveying exporters on Great.gov.uk to better
                understand their exporting experience and needs. This will help
                the Department to better support exporters across the country.
              </p>
            ) : (
              <p className="m-v-xs">
                You left the survey partly completed. It would be a great help
                to us if you could complete the survey now.
              </p>
            )}
            <p className="m-v-xs">
              It will take about 3-5 minutes to complete.
            </p>
            <a href="/privacy-policy/">
              This information is stored and used in compliance with our cookie
              and privacy policy.
            </a>
          </>
        }
        primaryButtonLabel="Continue"
        primaryButtonClick={() => setMode(modes.question)}
        secondaryButtonLabel="Not now"
        secondaryButtonClick={closeModal}
        closeClick={closeModal}
      />
    )

  if (mode === modes.question)
    return (
      <Modal
        className="segmentation-modal"
        title={question.title}
        body={
          <Interaction
            question={question}
            value={value}
            setValue={setValue}
          />
        }
        progressPercentage={
          question && questions && 100 * (questionIndex() / questions.length)
        }
        primaryButtonLabel="Next"
        primaryButtonClick={setQuestionAnswer}
        primaryButtonDisable={!value}
        secondaryButtonLabel="Back"
        secondaryButtonClick={goBack}
        closeClick={closeModal}
      />
    )
  if (mode === modes.thankyou)
    return (
      <Modal
        className="segmentation-modal"
        title="Thank you"
        body="Thank you for taking time to respond."
        primaryButtonLabel="Close"
        primaryButtonClick={closeModal}
        progressPercentage={100}
        secondaryButtonLabel="Back"
        secondaryButtonClick={goBack}
      />
    )
  return null
}

Questionnaire.propTypes = {
  handleModalClose: PropTypes.func,
}

Questionnaire.defaultProps = {
  handleModalClose: null,
}
