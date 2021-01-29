import React, { useState } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'

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
      })
      .catch(() => {})
  }

  return (
    <>
      <h3 className="h-m text-white m-b-xs">Section complete?</h3>
      <div className="great-checkbox great-checkbox--large great-checkbox--section-complete">
        <input
          type="checkbox"
          id="checkbox_complete"
          onChange={toggleComplete}
          checked={isComplete ? true : false}
        />
        <label htmlFor="checkbox_complete">Yes</label>
      </div>
    </>
  )
}

SectionComplete.propTypes = {
  current_section: PropTypes.shape({
    is_complete: PropTypes.bool.isRequired,
    url: PropTypes.string.isRequired,
    title: PropTypes.string,
    lessons: PropTypes.arrayOf(PropTypes.string),
    disabled: PropTypes.bool,
  }),
}
