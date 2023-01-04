import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'

import SurveyModal from './Modal'

// TODO
// - Set cookies when users close or finish the survey
// - Add name to question model - for use by radio buttons - could do this dynamically?

const orderQuestions = (questions) => (
    questions.sort((q1, q2) => (
        q1.order - q2.order
    ))
)

function ExporterSurvey() {
    const modes = { closed: 'c', start: 's', question: 'q', thankyou: 't' }
    const [mode, setMode] = useState(modes.start)
    const [questions, setQuestions] = useState([])
    const [currentQuestion, setCurrentQuestion] = useState()
    const [runningOrder, setRunningOrder] = useState([])

    useEffect(() => {
        Services.getSurveyDetails().then((survey) =>
            setQuestions(orderQuestions(survey.questions)))
    }, [])

    useEffect(() => {
        if (currentQuestion && !runningOrder.some((id) => id === currentQuestion.id)) {
            setRunningOrder([...runningOrder, currentQuestion.id])
        }
    }, [currentQuestion])

    const getQuestionById = (id) => (
        questions.find(q => q.id === id)
    )

    // TODO - Account for when there's a jump - do we need to add an 'end' option to jump options in API??
    const isFinalQuestion = () => questions.findIndex(q => q.id === currentQuestion.id) === (questions.length - 1)

    const startSurvey = () => {
        setMode(modes.question)
        setCurrentQuestion(questions[0])
    }

    const rejectSurvey = () => {
        // TODO - Set in user's cookie not to show survey
        console.log('Survey rejected')
        setMode(modes.closed)
    }

    const pauseSurvey = () => {
        // TODO - Set cookie to show survey one more time
        console.log('Set cookie to show survey once more')
        setMode(modes.closed)
    }

    const setValue = (answer) => {
        setCurrentQuestion({ ...currentQuestion, answer })
    }

    const getNextQuestion = () => {
        // TODO add logic to check if any validation errors
        // Can check using currentQuestion.answer

        const updatedQuestions = questions.map(q => q.id === currentQuestion.id ? { ...q, answer: currentQuestion.answer } : q)
        setQuestions(updatedQuestions)

        if (isFinalQuestion()) {
            // TODO - Set cookie to not show survey again
            // TODO - Send data to forms API here
            setMode(modes.thankyou)
            return
        }

        // TODO - Join this function and one below into two different ones:
        // One which handles getting answer and determine if there's a jump for list answers
        // One which handles it for string answers
        const getAnswerFromValue = () => {
            const { choices } = currentQuestion
            if (Array.isArray(currentQuestion.answer)) {
                return choices.filter(c => (currentQuestion.answer.includes(c.value)))
            }

            return choices.find((c) => c.value === currentQuestion.answer)

        }
        // If multiple answers have a jump - go to the first one
        // TODO - check this with someone
        const getAnswerJump = (answer) => {
            if (Array.isArray(answer)) {
                const answersWithJump = answer.filter(a => a.jump)
                if (answersWithJump.length) {
                    return Math.min(...answersWithJump.map(a => a.jump))
                }
                return null
            }
            return answer.jump
        }

        const answer = getAnswerFromValue()
        const answerJump = getAnswerJump(answer)
        const nextQuestionIndex = answerJump ?
            questions.findIndex((q) => q.id === currentQuestion.jump) :
            questions.findIndex((q) => q.id === currentQuestion.id) + 1

        setCurrentQuestion(questions[nextQuestionIndex])
    }

    const goBack = () => {
        const currentQuestionPosition = runningOrder.findIndex((q) => q === currentQuestion.id)

        if (currentQuestionPosition === 0) {
            setMode(modes.start)
        }
        else if (mode === modes.thankyou) {
            const previousQuestionId = runningOrder[runningOrder.length - 1]
            setCurrentQuestion(getQuestionById(previousQuestionId))
            setMode(modes.question)
        }
        else {
            const previousQuestionId = runningOrder[currentQuestionPosition - 1]
            setCurrentQuestion(getQuestionById(previousQuestionId))
        }
    }

    if (mode === modes.start) {
        return (
            <SurveyModal
                className="segmentation-modal"
                title="Help us serve you better"
                body={
                    <>
                        <p className="m-v-xs">
                            We&#39;re surveying exporters on Great.gov.uk to better
                            understand their exporting experience and needs. This will help
                            the Department to better support exporters across the country.
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
                primaryButtonClick={startSurvey}
                secondaryButtonLabel={"No, don't show me this again"}
                secondaryButtonClick={rejectSurvey}
                closeClick={pauseSurvey}
            />
        )
    }
    if (mode === modes.question) {
        return (
            questions.length && <SurveyModal
                className="segmentation-modal"
                title={currentQuestion.title}
                body={<Interaction question={currentQuestion} setValue={setValue} />}
                // TODO - change to be "Question x of x"
                progressPercentage={0.2}
                primaryButtonLabel="Next"
                primaryButtonClick={getNextQuestion}
                primaryButtonDisable={false}
                secondaryButtonLabel="Back"
                secondaryButtonClick={goBack}
                closeClick={rejectSurvey}
            />
        )
    }
    if (mode === modes.thankyou) {
        return (
            <SurveyModal
                className="segmentation-modal"
                title="Thank you"
                body={<>Thank you for taking time to respond.</>}
                primaryButtonLabel="Close"
                primaryButtonClick={() => setMode(modes.closed)}
                secondaryButtonLabel="Back"
                secondaryButtonClick={goBack}
            />
        )
    }
    return null
}

export default function createExportSurveyModal({ element }) {
    Modal.setAppElement(element)
    ReactDOM.render(<ExporterSurvey />, element)
}
