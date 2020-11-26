import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Total } from '../Costs/Total'
import { Costs } from '../Costs'

export const Direct = memo(({
  costs,
  total,
  currency
}) => {
  const perUnit = `${currency} per unit`
  return (
    <>
      <h2 className='h-m p-v-s'>Direct costs</h2>
      <p>These are the costs that go directly into building your product into something sellable. It is important you know your direct costs so you don't end up selling your product for less than you paid to make it.</p>
      <p>Record all of your direct costs in the table to calculate your total.</p>
      <Costs
        currency={perUnit}
        costs={costs}
      />
      <Total
        total={total}
        label='Direct costs total'
        currency={perUnit}
      />
    </>
  )
})

Direct.propTypes = {
  costs: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    heading: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
  })).isRequired,
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired
}

