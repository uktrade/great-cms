import React, { useState } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { analytics } from '@src/Helpers'

export const SectionComplete = ({ current_section }) => {
  const { is_complete, url } = current_section
  const current_section_slug = url.split('/')[3]
  const [isComplete, setIsComplete] = useState(is_complete)
  const toggleComplete = () => {
    const field_obj = {
      ui_progress: {
        [current_section_slug]: {
          is_complete: !isComplete,
        },
      },
    }
    update(field_obj)
  }

  const update = (field) => {
    Services.updateExportPlan(field)
      .then(() => {
        setIsComplete(!isComplete)
        if (!isComplete) {
          analytics({ event: 'planSectionComplete' })
        }
      })
      .catch(() => {})
  }

  const labelText = isComplete ? 'Great! Progress saved' : 'Yes'

  return (
    <>
      <h3 className="h-m text-white m-b-xs">Section complete?</h3>
      <div className="great-checkbox great-checkbox--large great-checkbox--section-complete">
        <input
          type="checkbox"
          id="checkbox_complete"
          onChange={toggleComplete}
          checked={isComplete}
        />
        <label htmlFor="checkbox_complete">
          {labelText}
        </label>
      </div>
    </>
  )
}
SectionComplete.propTypes = {
  current_section: PropTypes.shape({
    is_complete: PropTypes.bool,
    url: PropTypes.string,
  }).isRequired,
}
