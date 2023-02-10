import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Total = memo(({ total, currency, label }) => {
  return (
    <div className="costs costs--total">
      <span className="body-l-b">{label}</span>
      <span className="total">
        <span className="m-r-s">{currency}</span>
        <span className="body-l-b">{total}</span>
      </span>
    </div>
  )
})

Total.propTypes = {
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
}
