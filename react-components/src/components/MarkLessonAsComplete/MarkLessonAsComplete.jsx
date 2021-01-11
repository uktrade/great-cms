import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'

import Services from '../../Services'

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
      const dataLayer = (window.dataLayer = window.dataLayer || [])
      // adding tracking once lesson successfully updated as completed
      dataLayer.push({
        event: 'lessonComplete',
      })
    }
    setIsChecked(true)
  }

  return (
    <div className="mark-lesson-as-complete">
      <h3 className="h-m text-white p-b-s">Lesson complete?</h3>
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
        <label htmlFor="markascomplete_checkbox">{labelText}</label>
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
