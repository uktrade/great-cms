import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Input } from '@src/components/Form/Input'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCreditTotalExportCost = memo(({ ...data }) => {
  const { estimated_costs_per_unit, formData, currency } = data
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
            header: `Your estimate total export cost is GBP ${estimated_costs_per_unit}`,
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

  return (
    <>
      {estimated_costs_per_unit !== 0 ? (
        <p>
          To help you, we've created an estimate for you based on the figures
          you gave in on the Cost and pricing page.
        </p>
      ) : (
        <p>
          To get an estimate of your total export cost, complete the{' '}
          <a href="/export-plan/section/costs-and-pricing/">
            Costs and Pricing
          </a>{' '}
          section of your Export Plan. Once you're done, you'll see your
          estimate here.
        </p>
      )}
      <Input {...inputData} />
    </>
  )
})

FundingCreditTotalExportCost.propTypes = {
  estimated_costs_per_unit: PropTypes.number.isRequired,
  formData: PropTypes.object,
  currency: PropTypes.string.isRequired,
}
