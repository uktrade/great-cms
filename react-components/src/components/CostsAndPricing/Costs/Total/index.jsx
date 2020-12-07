import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Total = memo(({
  total,
  currency,
  label
}) => {
  return (
    <div className='costs costs--total bg-blue-deep-80 text-white'>
      <table className='m-t-0'>
        <tr>
          <td className='costs-label'>{label}</td>
          <td>
            <span className='body-l-b text-white m-r-s'>{total}</span>
            <span className='body-l-b text-white'>{currency}</span>
          </td>
        </tr>
      </table>
    </div>
  )
})

Total.propTypes = {
  total: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired
}
