import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { config } from '@src/config'
import { Input } from '@src/components/Form/Input'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCreditTotalExportCost = memo(({ ...data }) => {
  const { estimated_costs_per_unit, formData, currency } = data
  const { urlCostsAndPricing } = config
  const [formValue, setFormValue] = useState(
    formData['override_estimated_total_cost']
  )

  const update = (field) => {
    Services.updateExportPlan(field)
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const inputData = {
    onChange: (fieldItem) => {
      setFormValue(fieldItem['override_estimated_total_cost'])
      debounceUpdate({
        funding_and_credit: fieldItem,
      })
    },
    value: formValue,
    prepend: currency,
    hideLabel: true,
    label: 'Total export cost',
    id: 'override_estimated_total_cost',
    placeholder: '0',
    tooltip: null,
    type: 'number',
    field: 'override_estimated_total_cost',
    example:
      estimated_costs_per_unit !== 0
        ? {
            buttonTitle: 'Estimate',
            header: `Your estimate total export cost is GBP ${formValue}`,
            content: `<p>
        We calculated this by:
      </p>
      <ul class="list-bullet">
        <li>taking your total direct costs per unit</li>
        <li>multiplying it by the number of units you want to export in a year</li>
        <li>adding this to your overhead costs</li>
      </ul>
      <p>You may want to adjust this estimate, especially if your overhead costs aren't priced annually.</p>
      `,
          }
        : {},
  }

  return <Input {...inputData} />
})

FundingCreditTotalExportCost.propTypes = {
  estimated_costs_per_unit: PropTypes.number.isRequired,
  formData: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.shape({
      override_estimated_total_cost: PropTypes.number,
    }),
  ]).isRequired,
  currency: PropTypes.string.isRequired,
}

FundingCreditTotalExportCost.defaultProps = {
  formData: {
    override_estimated_total_cost: 0,
  },
}
