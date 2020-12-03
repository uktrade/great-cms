import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Total } from '../Costs/Total'
import { Costs } from '../Costs'

export const Overhead = memo(({
  costs,
  total,
  currency
}) => {
  return (
    <>
      <h2 className='h-m p-b-xs p-t-m'>Overhead costs</h2>
      <p>These are the ongoing costs associated with running your whole business operation. These costs are important to know as it will help you determine how much you charge for your product in order to make a profit.</p>
      <p>Record all of your overhead costs in the table to calculate your total.</p>
      <p className='g-panel'>You can enter up to 10 digits long value in each row in the table below.</p>
      <Costs
        costs={costs}
        currency={currency}
      />
      <Total
        total={total}
        label='Overhead costs total'
        currency={currency}
      />
    </>
  )
})

Overhead.propTypes = {
  costs: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    heading: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
  })).isRequired,
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired
}

