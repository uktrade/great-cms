import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'
import { FundingCreditOptions } from '@src/components/FundingCredit/FundingCreditOptions/FundingCreditOptions'
import { FundingCreditHowMuchFunding } from '@src/components/FundingCredit/FundingCreditHowMuchFunding/FundingCreditHowMuchFunding'

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
  // debugger
  const fundingCreditTotalExportCostData = [
    {
      name: 'financeTotalExportCost',
      field_type: 'NumberInput',
      currency: 'GBP',
      placeholder: '0.00',
    },
  ]

  const data = {
    ...params,
    formFields: fundingCreditTotalExportCostData,
  }
  ReactDOM.render(<FundingCreditHowMuchFunding {...data} />, element)
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
  ReactDOM.render(<FundingCreditOptions {...data} />, element)
}
