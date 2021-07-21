import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Cost } from './Cost'

export const Costs = memo(({ costs, currency, data, update }) => {
  return (
    <div className="costs costs--with-total bg-blue-deep-10">
      {costs.map(({ label, id, placeholder, tooltip, type, field }) => (
        <Cost
          key={id}
          label={label}
          id={id}
          currency={currency}
          placeholder={placeholder}
          tooltip={tooltip}
          value={data[id]}
          update={(x) => {
            const updatedField = type === 'number' ? { [id]: x[id] } : x
            update(x, { [field]: updatedField })
          }}
          type={type}
        />
      ))}
    </div>
  )
})

Costs.propTypes = {
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
  data: PropTypes.objectOf(PropTypes.any).isRequired,
  update: PropTypes.func.isRequired,
}
