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

  const labelText = isComplete && isChecked ? 'Progress saved' : 'Yes, track my progress'

  const markCompleted = () => {
    if (!isComplete) {
      // adding tracking once lesson successfully updated as completed
      analytics({ event: 'lessonComplete' })
    }
    setIsChecked(true)
  }

  

  return (
    <React.Fragment>
      <div class="govuk-form-group govuk-!-margin-top-4">
  <fieldset class="govuk-fieldset" aria-describedby="waste-hint">
    <legend class="govuk-fieldset__legend govuk-fieldset__legend--l govuk-!-margin-bottom-0">
      <h3 class="govuk-heading-m">
        Mark as complete?
      </h3>
    </legend>
    <div class="govuk-checkboxes" data-module="govuk-checkboxes">
      <div class="govuk-checkboxes__item">
        <input class="govuk-checkboxes__input" name="isComplete" type="checkbox" value='isCompelete'
          id="markascomplete_checkbox"
          onChange={() => {
            setIsComplete(!isComplete)
          }}
          onClick={markCompleted}
          checked={Boolean(isComplete)}
        />
        <label class="govuk-label govuk-checkboxes__label" for="isComplete">
          {labelText}
        </label>
      </div>
    </div>
  </fieldset>
</div>
</React.Fragment>
  )
}

MarkLessonAsComplete.propTypes = {
  endpoint: PropTypes.string.isRequired,
}

function createMarkLessonAsComplete({ element, endpoint }) {
  ReactDOM.render(<MarkLessonAsComplete endpoint={endpoint} />, element)
}

export { MarkLessonAsComplete, createMarkLessonAsComplete }
