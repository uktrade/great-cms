import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { FormElements } from '@src/components/FormElements'

export const FundingCreditTotalExportCost = memo(({ ...data }) => {
  const { estimated_costs_per_unit, formData, currency } = data

  const inputData = {
    prepend: currency,
    hideLabel: true,
    label: 'Total export cost',
    id: 'override_estimated_total_cost',
    placeholder: 0,
    field_type: 'NumberInput',
    field: 'override_estimated_total_cost',
    name: 'override_estimated_total_cost',
    example:
      estimated_costs_per_unit !== 0
        ? {
            buttonTitle: 'Estimate',
            header: `Your estimate total export cost is GBP ${formData.override_estimated_total_cost}`,
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
    <FormElements
      formFields={[inputData]}
      field="funding_and_credit"
      formData={formData}
    />
  )
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
