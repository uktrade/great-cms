import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { FormElements } from '@src/components/FormElements'

export const FundingCreditHowMuchFunding = memo(({ ...data }) => {
  const { estimated_costs_per_unit, formFields } = data

  const estimate = {
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

  formFields.map((item) => {
    return estimated_costs_per_unit
      ? { ...item, estimate: { ...(item.estimate = estimate) } }
      : item
  })

  return (
    <>
      <h3 className="h-s">Your total export cost</h3>
      <p>
        Your total export cost is how much it will cost your business to export
        for one year.
      </p>
      <p className="m-b-0">To work this out you will need:</p>
      <ul className="list-bullet m-t-xs">
        <li>your total direct costs per unit</li>
        <li>your total overhead costs</li>
        <li>the number of units you want to export</li>
      </ul>
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
      <FormElements {...data} />
    </>
  )
})

FundingCreditHowMuchFunding.propTypes = {
  estimated_costs_per_unit: PropTypes.number.isRequired,
}

// FundingCreditHowMuchFunding.defaultProps = {
//   estimated_costs_per_unit: 0,
// }
