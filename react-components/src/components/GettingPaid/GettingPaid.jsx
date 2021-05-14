import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { formatLessonLearned } from '@src/Helpers'
import { useUpdateExportPlan } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'
import ErrorList from '@src/components/ErrorList'

export const GettingPaid = memo(
  ({ formFields, formData, field, lessonDetails, currentSection }) => {
    const [state, setState] = useState(formData)
    const [update, showMessage, pending, errors] = useUpdateExportPlan(field)

    const onChange = (updatedField, otherProps, section, isNotes = false) => {
      const note = isNotes ? { notes: updatedField[isNotes] } : updatedField

      setState({
        ...state,
        [section]: {
          ...state[section],
          ...note,
        },
      })

      update({ [field]: { [section]: { ...note, ...otherProps } } })
    }

    return (
      <div className="target-market-documents-form">
        {formFields.map(({ group, field: key }, i) => {
          const select = group[0]
          const textarea = group[1]
          const selected =
            (state[key] && state[key][select.id]) ||
            (select.multiSelect ? [] : '')
          return (
            <div className="user-form-group" key={select.id}>
              <Select
                label={select.label}
                id={select.id}
                name={select.name}
                options={select.options}
                selected={selected}
                update={(data) => {
                  onChange(
                    { [select.id]: data[select.id] },
                    { notes: state[key] ? state[key].notes : '' },
                    key
                  )
                }}
                placeholder="select multiple"
                multiSelect={select.multiSelect}
                lesson={formatLessonLearned(lessonDetails, currentSection, i)}
              />
              <TextArea
                onChange={(data) =>
                  onChange(data, { [select.id]: selected }, key, textarea.id)
                }
                label={textarea.label}
                id={textarea.id}
                value={state[key] ? state[key].notes : ''}
                placeholder={textarea.placeholder}
              />
            </div>
          )
        })}
        <ErrorList errors={errors.__all__ || []} className="m-t-s" />
      </div>
    )
  }
)

GettingPaid.propTypes = {
  formFields: PropTypes.arrayOf(
    PropTypes.objectOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(
          PropTypes.shape({
            value: PropTypes.string,
            label: PropTypes.string,
          })
        ),
      ])
    )
  ).isRequired,
  formData: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.objectOf(
        PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.arrayOf(PropTypes.string),
        ])
      ),
    ])
  ).isRequired,
  field: PropTypes.string.isRequired,
  lessonDetails: PropTypes.oneOfType([PropTypes.string]).isRequired,
  currentSection: PropTypes.shape({
    url: PropTypes.string,
    lessons: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
}
