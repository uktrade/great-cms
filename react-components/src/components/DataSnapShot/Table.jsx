import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'

export const Table = memo(({
  population,
  targetPopulation,
}) => (
  <div className='target-age-group-insights table m-t-s'>
    <div className='grid'>
      <div className='c-1-2'>
        <Stats
          header='Total population'
          data={population ? `${population} million` : notAvailable }
        />
      </div>
      <div className='c-1-2'>
        <Stats
          header='Target age population'
          data={targetPopulation ? `${targetPopulation} million` : notAvailable }
        />
      </div>
    </div>
  </div>
))

Table.propTypes = {
  population: PropTypes.number.isRequired,
  targetPopulation: PropTypes.number.isRequired,
}
