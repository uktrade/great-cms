import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCreditHowMuchFunding = memo(({ ...data }) => {
  const { formFields, currency, value } = data
  const [formValue, setFormValue] = useState(value)

  const update = (field, value) => {
    Services.updateFundingCreditOption({ ...field, ...value })
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const inputData = {
    onChange: (e) => {
      debugger
      setFormValue(e['how_much_funding'])
      debounceUpdate(e)
    },
    value: formValue,
    prepend: currency,
    hideLabel: true,
    label: 'How much funding you need',
    id: 'how_much_funding',
    placeholder: '0',
    tooltip: null,
    type: 'number',
    field: 'how_much_funding',
  }

  return (
    <>
      <Input {...inputData} />
    </>
  )
})

FundingCreditHowMuchFunding.propTypes = {}

// FundingCreditHowMuchFunding.defaultProps = {
//   estimated_costs_per_unit: 0,
// }
