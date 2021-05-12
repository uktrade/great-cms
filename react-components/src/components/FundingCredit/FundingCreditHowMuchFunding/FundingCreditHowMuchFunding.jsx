import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { formatLessonLearned } from '@src/Helpers'
import { FormElements } from '@src/components/FormElements'

export const FundingCreditHowMuchFunding = memo(({ ...data }) => {
  const { formData, currency, lessonDetails, currentSection } = data

  const inputData = {
    prepend: currency,
    hideLabel: true,
    label: 'How much funding you need',
    id: 'funding_amount_required',
    placeholder: 0,
    field_type: 'NumberInput',
    field: 'funding_amount_required',
    name: 'funding_amount_required',
    lesson: formatLessonLearned(lessonDetails, currentSection, 0),
  }

  return (
    <FormElements
      formFields={[inputData]}
      field="funding_and_credit"
      formData={formData}
    />
  )
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
