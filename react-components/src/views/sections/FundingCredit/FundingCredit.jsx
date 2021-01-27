import React from 'react'
import ReactDOM from 'react-dom'

import { FundingCreditHowMuchFunding } from '@src/components/FundingCredit/FundingCreditHowMuchFunding/FundingCreditHowMuchFunding'
import { FundingCreditTotalExportCost } from '@src/components/FundingCredit/FundingCreditTotalExportCost/FundingCreditTotalExportCost'
import { FundingCreditOptions } from '@src/components/FundingCredit/FundingCreditOptions/FundingCreditOptions'

export const fundingCreditTotalExportCost = ({ element, ...params }) => {
  debugger
  ReactDOM.render(<FundingCreditTotalExportCost {...params} />, element)
}

export const fundingCreditHowMuchFunding = ({ element, ...params }) => {
  ReactDOM.render(<FundingCreditHowMuchFunding {...params} />, element)
}

export const fundingCreditFundingCreditOptions = ({ element, ...params }) => {
  const { options } = params
  const fundingCreditOptions = {
    id: 'funding_option',
    name: 'funding_option',
    placeholder: 'Select option',
    options,
  }
  const data = {
    ...params,
    fundingCreditOptions,
  }
  ReactDOM.render(<FundingCreditOptions {...data} />, element)
}
