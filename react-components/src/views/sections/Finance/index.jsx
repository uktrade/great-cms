import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'

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

const financeFundingCreditOptionsData = [
  {
    name: 'financeFundingCreditOptions',
    label: 'Test label',
  },
]

export const financeTotalExportCost = ({ element, ...params }) => {
  const data = {
    ...params,
    formFields: financeTotalExportCostData,
  }
  ReactDOM.render(<FormElements {...data} />, element)
}

export const financeHowMuchFunding = ({ element, ...params }) => {
  const data = {
    ...params,
    formFields: financeHowMuchFundingData,
  }
  ReactDOM.render(<FormElements {...data} />, element)
}

export const financeFundingCreditOptions = ({ element, ...params }) => {
  const data = {
    ...params,
    formFields: financeFundingCreditOptionsData,
  }
  ReactDOM.render(<FormElements {...data} />, element)
}
