import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { analytics } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import Services from '../../Services'

export const SpendingAndResources = ({ field, formFields, formData }) => {
  const [input, setInput] = useState(formData)
  const [pushedAnalytic, setPushedAnalytic] = useState(false)

  const update = (e) => {
    Services.updateExportPlan({ [field]: { ...e } })
      .then(() => {
        if (!pushedAnalytic) {
          analytics({
            event: 'planSectionSaved',
            sectionTitle: 'marketing-approach',
          })
          setPushedAnalytic(true)
        }
      })
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (e) => {
    setInput({ ...e })
    debounceUpdate(e)
  }

  return (
    <>
      {formFields.map((item) => (
        <TextArea
          label={item.label}
          example={{ content: item.example }}
          key={item.name}
          id={item.name}
          value={input[item.name]}
          description={item.description}
          placeholder={
            Number.isInteger(item.placeholder)
              ? item.placeholder
              : 'Add some text'
          }
          currency={item.currency}
          tag={Number.isInteger(item.placeholder) ? 'number' : 'text'}
          onChange={onChange}
        />
      ))}
    </>
  )
}

SpendingAndResources.propTypes = {
  field: PropTypes.string.isRequired,
  formData: PropTypes.objectOf(PropTypes.string).isRequired,
  formFields: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      placeholder: PropTypes.string.isRequired,
    })
  ).isRequired,
}
