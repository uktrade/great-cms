import React from 'react'
import ReactDOM from 'react-dom'

import { FundingCreditHowMuchFunding } from '@src/components/FundingCredit/FundingCreditHowMuchFunding/FundingCreditHowMuchFunding'
import { FundingCreditTotalExportCost } from '@src/components/FundingCredit/FundingCreditTotalExportCost/FundingCreditTotalExportCost'
import { FundingCreditOptions } from '@src/components/FundingCredit/FundingCreditOptions/FundingCreditOptions'

export const fundingCreditTotalExportCost = ({ element, ...params }) => {
  debugger
  const data = {
    ...params,
  }
  ReactDOM.render(<FundingCreditTotalExportCost {...data} />, element)
}

export const fundingCreditHowMuchFunding = ({ element, ...params }) => {
  const data = {
    ...params,
  }
  ReactDOM.render(<FundingCreditHowMuchFunding {...data} />, element)
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
