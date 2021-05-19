import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { mapArray } from '@src/Helpers'
import Interaction from './Interaction'
import Modal from './Modal'
import CompanyNameModal from './CompanyNameModal'

export default function Questionnaire(props) {
  const modes = { closed: 'c', start: 's', question: 'q', thankyou: 't' }
  const { handleModalClose } = props
  const [mode, setMode] = useState(modes.closed)
  const [question, _setQuestion] = useState()
  const [runningState, setRunningState] = useState({ questions: [] })

  const closeModal = () => {
    setMode(modes.closed)
    handleModalClose()
  }

  const questionOptions = (q) =>
    (q && q.choices && Array.isArray(q.choices)
      ? q.choices
      : q.choices.options) || []

  const questionIndex = () =>
    question && runningState.questions.findIndex((q) => q.id === question.id)

  const setValue = (answer) => {
    _setQuestion({ ...question, answer })
  }

  const setQuestion = (newQuestion) => {
    if (newQuestion && mode === modes.closed) setMode(modes.start)
    if (!newQuestion) setMode(modes.thankyou)
    _setQuestion(newQuestion)
  }

  const processAnswers = (questionnaire) => {
    if (questionnaire && questionnaire.questions) {
      const sorted = questionnaire.questions.sort((q1, q2) => {
        return q1.order > q2.order ? 1 : -1
      })
      // Work out first unanswered question
      const answers = mapArray(questionnaire.answers, 'question_id')
      const status = sorted.reduce((last, loopQuestion) => {
        const answered = answers[loopQuestion.id]
        const out = { ...last }
        if (answered) {
          // We want to decorate the questions with answers so stop eslint moaning
          /* eslint-disable no-param-reassign */
          loopQuestion.answer = answered.answer
          /* eslint-enable no-param-reassign */
          if (!out.jump) {
            out.lastAnswered = loopQuestion
            // see if this has a jump answer
            const choice = questionOptions(loopQuestion).find(
              (option) => option.value === loopQuestion.answer
            )
            out.jump = choice && choice.jump
          }
        } else {
          out.firstUnanswered = out.firstUnanswered || loopQuestion
        }
        return out
      }, {})
      setRunningState({ questions: sorted, ...status, loaded: true })
    }
  }

  useEffect(() => {
    // On a change in questionnaire state, set the next question )
    if (runningState.loaded) {
      const terminated = runningState.jump === 'end'
      if (question) {
        // follwing saving an answer
        const nextQuestion = runningState.questions[questionIndex() + 1]
        if (!nextQuestion || terminated) {
          // Questionnaire completed
          setQuestion(null)
        } else {
          setQuestion(nextQuestion)
        }
      } else {
        setQuestion(!terminated && runningState.firstUnanswered)
      }
    }
  }, [runningState])

  useEffect(() => {
    Services.getUserQuestionnaire().then(processAnswers)
  }, [])

  const goBack = () => {
    let newQuestion = runningState.questions[questionIndex() - 1]
    if (mode === modes.thankyou) {
      setMode(modes.question)
      newQuestion = runningState.lastAnswered
    }
    if (!newQuestion) {
      setMode(modes.start)
    } else {
      setQuestion(newQuestion)
    }
  }

  const setQuestionAnswer = () => {
    Services.setUserQuestionnaireAnswer(question.id, question.answer)
      .then(processAnswers)
      .catch(() => {})
  }

  const completeQuestionnaire = () => {
    Services.setUserQuestionnaireAnswer(0, 'complete')
    closeModal()
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
            <a
              href="/privacy-and-cookies/"
              target="_blank"
              title="Opens in a new window"
              rel="noopener noreferrer"
              className="link link--underline body-l"
            >
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

  if (mode === modes.question && question.type !== 'COMPANY_LOOKUP')
    return (
      <Modal
        className="segmentation-modal"
        title={question.title}
        body={<Interaction question={question} setValue={setValue} />}
        progressPercentage={
          question && 100 * (questionIndex() / runningState.questions.length)
        }
        primaryButtonLabel="Next"
        primaryButtonClick={setQuestionAnswer}
        primaryButtonDisable={!question.answer || !question.answer.length}
        secondaryButtonLabel="Back"
        secondaryButtonClick={goBack}
        closeClick={closeModal}
      />
    )
  if (mode === modes.question && question.type === 'COMPANY_LOOKUP')
    return (
      <CompanyNameModal
        question={question}
        value={question.answer}
        setValue={setValue}
        nextButtonClick={setQuestionAnswer}
        backButtonClick={goBack}
        closeClick={closeModal}
        progressPercentage={
          question && 100 * (questionIndex() / runningState.questions.length)
        }
      />
    )
  if (mode === modes.thankyou)
    return (
      <Modal
        className="segmentation-modal"
        title="Thank you"
        body={<>Thank you for taking time to respond.</>}
        primaryButtonLabel="Close"
        primaryButtonClick={completeQuestionnaire}
        secondaryButtonLabel="Back"
        secondaryButtonClick={goBack}
        progressPercentage={100}
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
