import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { getLabel, getLabels, getValue, getValues } from '@src/Helpers'
import { useUpdateExportPlan } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'

export const GettingPaid = memo(({ formFields, formData, field }) => {
  const [state, setState] = useState(formData)
  const [update] = useUpdateExportPlan(field)

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
      {formFields.map(({ group, field: key }) => {
        const select = group[0]
        const textarea = group[1]
        const options = Array.isArray(select.options)
          ? select.options
          : Object.keys(select.options).flatMap((x) => select.options[x])
        const selected = select.multiSelect
          ? getLabels(options, state[key] ? state[key][select.id] : [])
          : getLabel(options, state[key] ? state[key][select.id] : '')

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
                  {
                    [select.id]: select.multiSelect
                      ? getValues(select.options, data[select.id])
                      : data[select.id],
                  },
                  { notes: state[key] ? state[key].notes : '' },
                  key
                )
              }}
              multiSelect={select.multiSelect}
            />
            <TextArea
              onChange={(data) =>
                onChange(
                  data,
                  {
                    [select.id]: select.multiSelect
                      ? getValues(options, selected)
                      : getValue(options, selected),
                  },
                  key,
                  textarea.id
                )
              }
              label={textarea.label}
              id={textarea.id}
              value={state[key] ? state[key].notes : ''}
              placeholder={textarea.placeholder}
            />
          </div>
        )
      })}
    </div>
  )
})

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
}
