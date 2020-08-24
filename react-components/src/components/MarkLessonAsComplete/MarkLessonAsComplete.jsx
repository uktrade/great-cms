import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'

import Services from '../../Services'

const MarkLessonAsComplete = ({ endpoint }) => {
  const [isComplete, setIsComplete] = useState(undefined)
  const [isChecked, setIsChecked] = useState(false)

  useEffect(() => {
    if (isComplete === undefined) {
      Services.getLessonComplete(endpoint)
        .then((response) => response.json())
        .then(({ lesson_completed }) => {
          if (lesson_completed.length >= 1) {
            setIsComplete(true)
          }
        })
        .then(() => {})
        .catch(() => {})
    } else {
      Services[isComplete ? 'setLessonComplete' : 'setLessonIncomplete'](endpoint)
        .then(() => {})
        .catch(() => {})
    }
  }, [isComplete])

  const labelText = isComplete && isChecked ? 'Great! Progress saved' : 'Yes'

  return (
    <div className="mark-lesson-as-complete">
      <h3 className="h-l text-white p-b-s">Lesson complete?</h3>
      <div className="great-checkbox great-checkbox--large">
        <input
          type="checkbox"
          id="markascomplete_checkbox"
          onChange={() => {
            setIsComplete(!isComplete)
          }}
          onClick={() => setIsChecked(true)}
          checked={Boolean(isComplete)}
        />
        <label htmlFor="markascomplete_checkbox">{labelText}</label>
      </div>
    </div>
  )
}

function createMarkLessonAsComplete({ element, endpoint }) {
  ReactDOM.render(<MarkLessonAsComplete endpoint={endpoint} />, element)
}

export { MarkLessonAsComplete, createMarkLessonAsComplete }
