import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import { millify } from '@src/Helpers'

const formatNumber = (val) => val ? millify(val*1000) : notAvailable
export const Table = memo(({ totalPopulation, totalTargetAgePopulation }) => (
  <div className="m-t-s">
    <div className="grid stat-group">
      <div className="c-1-2">
        <Stats
          header="Total population"
          data={formatNumber(totalPopulation)}
        />
      </div>
      <div className="c-1-2">
        <Stats
          header="Target age population"
          data={formatNumber(totalTargetAgePopulation)}
        />
      </div>
    </div>
  </div>
))

Table.propTypes = {
  totalPopulation: PropTypes.number,
  totalTargetAgePopulation: PropTypes.number,
}
Table.defaultProps = {
  totalPopulation: null,
  totalTargetAgePopulation: null,
}
