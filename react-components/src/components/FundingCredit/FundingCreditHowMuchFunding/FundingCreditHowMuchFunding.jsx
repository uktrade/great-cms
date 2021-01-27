import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCreditHowMuchFunding = memo(({ ...data }) => {
  const { formData, currency } = data
  const [formValue, setFormValue] = useState(
    formData['funding_amount_required']
  )

  const update = (field) => {
    Services.updateExportPlan(field)
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const inputData = {
    onChange: (fieldItem) => {
      setFormValue(fieldItem['funding_amount_required'])
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
    tooltip: null,
    type: 'number',
    field: 'funding_amount_required',
  }

  return <Input {...inputData} />
})

FundingCreditHowMuchFunding.propTypes = {
  formData: PropTypes.object,
  currency: PropTypes.string.isRequired,
}

FundingCreditHowMuchFunding.defaultProps = {
  formData: {
    funding_amount_required: 0,
  },
}
