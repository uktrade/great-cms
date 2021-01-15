import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Total } from './Total'
import { Options } from './Options'
import { fundingCreditOptions } from '../constants'

// const fundingCreditOptions = {
//   id: 'funding_option',
//   name: 'select option',
//   placeholder: 'Select option',
//   currency: 'GBP',
//   type: 'number',
//   value: 0,
//   options: [
//     { value: 'bank', label: 'Bank loan' },
//     { value: 'gov', label: 'Finance support from government' },
//     { value: 'platform', label: 'Finance platforms' },
//     { value: 'peer', label: 'Peer-to-peer loan' },
//     { value: 'equity', label: 'Equity finance' },
//     { value: 'other', label: 'other' },
//   ],
// }

export const FundingCredit = memo(({ formFields, currency }) => {
  return (
    <>
      <Options
        formFields={formFields}
        currency={currency}
        selectData={fundingCreditOptions}
      />
      <Total label="Total funding" />
    </>
  )
})

// FundingCredit.propTypes = {
//   costs: PropTypes.arrayOf(
//     PropTypes.shape({
//       label: PropTypes.string.isRequired,
//       id: PropTypes.string.isRequired,
//       heading: PropTypes.string.isRequired,
//       description: PropTypes.string.isRequired,
//     })
//   ).isRequired,
//   currency: PropTypes.string.isRequired,
//   data: PropTypes.objectOf(PropTypes.number).isRequired,
//   update: PropTypes.func.isRequired,
// }
