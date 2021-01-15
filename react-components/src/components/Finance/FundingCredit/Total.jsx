import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Total = memo(({ total, currency, label }) => {
  return (
    <div className="costs costs--total bg-blue-deep-80 text-white">
      <table className="m-t-0">
        <tr>
          <td>{label}</td>
          <td className="total">
            <span className="text-white m-r-s">{currency}</span>
            <span className="body-l-b text-white">{total}</span>
          </td>
        </tr>
      </table>
    </div>
  )
})

Total.propTypes = {
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
}
