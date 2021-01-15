import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Total } from './Total'
import { Options } from './Options'

export const FundingCredit = memo(({ costs, currency, data, update }) => {
  const perUnit = `${currency} per unit`
  return (
    <>
      <Options
        currency={perUnit}
        options={options}
        data={data}
        update={update}
      />
      <Total
        total={data.direct_total}
        label="Direct costs total"
        currency={perUnit}
      />
    </>
  )
})

Direct.propTypes = {
  costs: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
      heading: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
    })
  ).isRequired,
  currency: PropTypes.string.isRequired,
  data: PropTypes.objectOf(PropTypes.number).isRequired,
  update: PropTypes.func.isRequired,
}
