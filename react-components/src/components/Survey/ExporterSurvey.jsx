import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'
import Services from '@src/Services'
import Interaction from './Interaction'

import SurveyModal from './Modal'

// TODO
// - Order questions by question.order
// - Set mode to start when land on page
// - Add name to question model - for use by radio buttons - could do this dynamically?


// Potential state:
// - Questions
// - Current question
// - Answered questions
// - Last answered question?
// - Mode (open, question, finish)


function ExporterSurvey() {
    const [questions, setQuestions] = useState([])
    useEffect(() => {
        Services.getSurveyDetails().then((survey) =>
            setQuestions(survey.questions))
    }, [])
    const question = questions[0]
    return (
        questions.length && <SurveyModal
            className="segmentation-modal"
            title={question.title}
            body={<Interaction question={question} setValue={() => console.log('Set value')} />}
            progressPercentage={0.2
                // question && 100 * (questionIndex() / runningState.questions.length)
            }
            primaryButtonLabel="Next"
            primaryButtonClick={() => console.log('Primary button click')}
            primaryButtonDisable={false}
            secondaryButtonLabel="Back"
            secondaryButtonClick={() => console.log('go Back')}
            closeClick={() => console.log('close modal')}
        />
    )
}

export default function createExportSurveyModal({ element }) {
    Modal.setAppElement(element)
    ReactDOM.render(<ExporterSurvey />, element)
}
