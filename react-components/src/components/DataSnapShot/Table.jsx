import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import { millify } from '@src/Helpers'

const formatNumber = (val) => (val-0 === val) ? millify(val) : notAvailable

export const Table = memo(({ totalPopulation, target }) => (
  <div className="stat-group m-t-xs">
    <div className="grid">
      <div className="c-1-2">
        <Stats
          header="Total population"
          data={formatNumber(totalPopulation)}
        />
      </div>
      <div className="c-1-2">
        <Stats
          header="Target age population"
          data={formatNumber(target)}
        />
      </div>
    </div>
  </div>
))

Table.propTypes = {
  totalPopulation: PropTypes.number,
  target: PropTypes.number,
}
Table.defaultProps = {
  totalPopulation: null,
  target: null,
}
