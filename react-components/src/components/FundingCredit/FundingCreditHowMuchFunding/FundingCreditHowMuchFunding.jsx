import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { formatLessonLearned } from '@src/Helpers'

export const FundingCreditHowMuchFunding = memo(({ ...data }) => {
  const { formData, currency, lessonDetails, currentSection } = data
  const [formValue, setFormValue] = useState(formData.funding_amount_required)

  const update = (field) => {
    Services.updateExportPlan(field)
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const inputData = {
    onChange: (fieldItem) => {
      setFormValue(fieldItem.funding_amount_required)
      debounceUpdate({
        funding_and_credit: fieldItem,
      })
    },
    value: formValue,
    prepend: currency,
    hideLabel: true,
    label: 'How much funding you need',
    id: 'funding_amount_required',
    placeholder: '0',
    type: 'number',
    field: 'funding_amount_required',
    lesson: formatLessonLearned(lessonDetails, currentSection, 0),
  }

  return <Input {...inputData} />
})

FundingCreditHowMuchFunding.propTypes = {
  formData: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.shape({
      funding_amount_required: PropTypes.number,
    }),
  ]).isRequired,
  currency: PropTypes.string.isRequired,
  lessonDetails: PropTypes.oneOfType([PropTypes.string]).isRequired,
  currentSection: PropTypes.shape({
    url: PropTypes.string,
    lessons: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
}

FundingCreditHowMuchFunding.defaultProps = {
  formData: {
    funding_amount_required: 0,
  },
}
