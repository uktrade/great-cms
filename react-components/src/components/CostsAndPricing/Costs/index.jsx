import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Cost } from './Cost'

export const Costs = memo(({
  costs,
  currency,
  data,
  update
}) => {
  return (
    <div className='costs bg-blue-deep-10'>
      <table className='m-b-0'>
        {costs.map(({ label, id, heading, description}) => (
          <Cost
            key={id}
            label={label}
            id={id}
            currency={currency}
            heading={heading}
            description={description}
            value={data[id]}
            update={update}
          />
        ))}
      </table>
    </div>
  )
})

Costs.propTypes = {
  costs: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    heading: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
  })).isRequired,
  currency: PropTypes.string.isRequired,
  data: PropTypes.objectOf(PropTypes.number).isRequired,
  update: PropTypes.func.isRequired,
}
