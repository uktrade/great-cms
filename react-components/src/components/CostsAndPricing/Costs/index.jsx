import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Cost } from './Cost'

export const Costs = memo(({ costs, currency, data, update }) => {
  return (
    <div className="costs bg-blue-deep-10">
      <table className="m-b-0">
        <tbody>
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
                const updatedField =
                  type === 'number' ? { [id]: Number(x[id]).toFixed(2) } : x
                update(x, { [field]: updatedField })
              }}
              type={type}
            />
          ))}
        </tbody>
      </table>
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
