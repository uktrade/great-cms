import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Total = memo(({ total, currency, label }) => {
  return (
    <div className="costs costs--total bg-blue-deep-80 text-white">
      <span className="body-l-b text-white">{label}</span>
      <span className="total">
        <span className="text-white m-r-s">{currency}</span>
        <span className="body-l-b text-white">{total}</span>
      </span>
    </div>
  )
})

Total.propTypes = {
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
}
