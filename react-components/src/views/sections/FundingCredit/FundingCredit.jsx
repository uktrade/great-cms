import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'
import { FundingCreditOptions } from '@src/components/FundingCredit/FundingCreditOptions/FundingCreditOptions'

const financeTotalExportCostData = [
  {
    name: 'financeTotalExportCost',
    field_type: 'NumberInput',
    currency: 'GBP',
    placeholder: '0.00',
    estimate: {
      header: 'Your estimate total export cost is GBP 0.00.',
      content: `
        <p>
          We calculated this by:
        </p>
        <ul class="list-bullet">
          <li>taking your total direct costs per unit</li>
          <li>multiplying it by the number of units you want to export in a year</li>
          <li>adding this to your overhead costs</li>
        </ul>
        <p>You may want to adjust this estimate, especially if your overhead costs aren't priced annually.</p>
      `,
    },
  },
]

const financeHowMuchFundingData = [
  {
    name: 'financeHowMuchFunding',
    field_type: 'NumberInput',
    currency: 'GBP',
    placeholder: '0.00',
    tooltip: `<p>Some tooltip here</p>`,
  },
]

export const fundingCreditTotalExportCost = ({ element, ...params }) => {
  debugger
  const data = {
    ...params,
    formFields: financeTotalExportCostData,
  }
  ReactDOM.render(<FormElements {...data} />, element)
}

export const fundingCreditHowMuchFunding = ({ element, ...params }) => {
  const data = {
    ...params,
    formFields: financeHowMuchFundingData,
  }
  ReactDOM.render(<FormElements {...data} />, element)
}

export const fundingCreditFundingCreditOptions = ({ element, ...params }) => {
  const { options } = params
  const fundingCreditOptions = {
    id: 'funding_option',
    name: 'funding_option',
    placeholder: 'Select option',
    options: options,
  }
  const data = {
    ...params,
    fundingCreditOptions,
  }
  debugger
  ReactDOM.render(<FundingCreditOptions {...data} />, element)
}
