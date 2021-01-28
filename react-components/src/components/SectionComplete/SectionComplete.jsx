import React, { useState } from 'react'
import ReactDOM from 'react-dom'
// import PropTypes from 'prop-types'
import Services from '@src/Services'

export const SectionComplete = ({ ...params }) => {
  const { current_section } = params
  const current_section_slug = current_section.url.split('/')[3]
  const [isComplete, setIsComplete] = useState(current_section.is_complete)

  // debugger
  const toggleComplete = () => {
    setIsComplete(!isComplete)

    const field_obj = {
      ui_progress: {
        [current_section_slug]: {
          is_complete: isComplete,
        },
      },
    }

    update(field_obj)
  }

  const update = (field) => {
    Services.updateExportPlan(field)
      .then(() => {})
      .catch(() => {})
  }

  return (
    <button
      type="button"
      className="button button--tertiary"
      onClick={toggleComplete}
    >
      You complete me. Currently {current_section_slug} :{' '}
      {!isComplete ? 'True' : 'False'}.
    </button>
  )
}
