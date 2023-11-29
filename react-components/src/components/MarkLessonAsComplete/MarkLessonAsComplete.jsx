import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { analytics } from '@src/Helpers'

const MarkLessonAsComplete = ({ endpoint }) => {
  const [isComplete, setIsComplete] = useState(undefined)
  const [persistedIsComplete, setPersistedIsComplete] = useState()
  const [isChecked, setIsChecked] = useState(false)

  useEffect(() => {
    if (isComplete === undefined) {
      Services.getLessonComplete(endpoint)
        .then((response) => response.json())
        .then(({ lesson_completed }) => {
          if (lesson_completed.length >= 1) {
            setPersistedIsComplete(true)
            setIsComplete(true)
          }
        })
        .then(() => {})
        .catch(() => {})
    } else if (persistedIsComplete !== isComplete) {
      Services[isComplete ? 'setLessonComplete' : 'setLessonIncomplete'](
        endpoint
      ).finally(() => {
        setPersistedIsComplete(isComplete)
      })
    }
  }, [isComplete])

  const labelText = isComplete && isChecked ? 'Great! Progress saved' : 'Yes'

  const markCompleted = () => {
    if (!isComplete) {
      // adding tracking once lesson successfully updated as completed
      analytics({ event: 'lessonComplete' })
    }
    setIsChecked(true)
  }

  return (
    <div className="mark-lesson-as-complete">
      <legend>
        <h2 className="govuk-heading-l govuk-!-margin-top-8 govuk-!-margin-bottom-4 great-text-white great-font-size-28" aria-hidden="true">Lesson complete?</h2>
      </legend>
      <div className="great-checkbox great-checkbox--large">
        <input
          type="checkbox"
          id="markascomplete_checkbox"
          onChange={() => {
            setIsComplete(!isComplete)
          }}
          onClick={markCompleted}
          checked={Boolean(isComplete)}
        />
        <label htmlFor="markascomplete_checkbox"><span className="visually-hidden">Lesson complete?</span><span aria-hidden="true">{labelText}</span></label>
      </div>
    </div>
  )
}

MarkLessonAsComplete.propTypes = {
  endpoint: PropTypes.string.isRequired,
}

function createMarkLessonAsComplete({ element, endpoint }) {
  ReactDOM.render(<MarkLessonAsComplete endpoint={endpoint} />, element)
}

export { MarkLessonAsComplete, createMarkLessonAsComplete }
