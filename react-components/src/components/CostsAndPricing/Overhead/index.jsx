import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Total } from '../Costs/Total'
import { Costs } from '../Costs'

export const Overhead = memo(({ costs, currency, data, update }) => {
  return (
    <>
      <h2 className="h-m p-b-xs p-t-m">Overhead costs</h2>
      <p>
        These are the ongoing costs of creating your product. Knowing your
        overhead costs will help you figure out what to price your product to
        make a profit.
      </p>
      <p>Record your overhead costs in the table to calculate your total.</p>
      <Costs costs={costs} currency={currency} data={data} update={update} />
      <Total
        total={data.overhead_total}
        label="Overhead costs total"
        currency={currency}
      />
    </>
  )
})

Overhead.propTypes = {
  costs: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      id: PropTypes.string.isRequired,
      placeholder: PropTypes.string.isRequired,
      tooltip: PropTypes.objectOf(PropTypes.string),
      type: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
    })
  ).isRequired,
  currency: PropTypes.string.isRequired,
  data: PropTypes.objectOf(PropTypes.string).isRequired,
  update: PropTypes.func.isRequired,
}
