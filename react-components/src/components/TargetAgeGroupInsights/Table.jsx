import React, { memo } from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '../EducationalMomentTooltip'
import { Stats } from '@src/components/Stats'
import { StatsGroup, notAvailable } from '@src/components/Stats/StatsGroup'

export const Table = memo(({
  population,
  cpi,
  urban,
  rural,
  female,
  male,
  internetPercentage,
  internetTotal,
  targetPopulation,
  languages
}) => (
  <div className='m-t-m'>
    <div className='grid'>
      <h3 className='body-l-b m-b-xs'>Global demographic data</h3>
      <div className='c-1-3'>
        <Stats
          header='Total population'
          data={population ? `${population} million` : notAvailable }
        />
      </div>
      <div className='c-1-3'>
        <Stats
          header='Access to the internet (total)'
          data={internetPercentage ? `${internetPercentage}% (${internetTotal} million)` : notAvailable}
        />
      </div>
      <div className='c-1-3'>
        <Stats
          header='Consumer Price Index'
          data={cpi || notAvailable }
        >
          <EducationalMomentTooltip
            id='corruption-perception-index-tooltip'
            heading='What is the Consumer Price Index?'
            description='The CPI measures the average change in prices over time that consumers pay for a basket of goods and services for their household, this is also known as inflation. It is used to estimate the change in total cost of this basket and the effect this has on the purchasing power of the country’s unit of currency.'
          />
        </Stats>
      </div>
    </div>

    <div className='grid'>
      <div className='c-full'>
        <Stats
          header='Languages in your target market'
          data={languages || notAvailable }
        />
      </div>
    </div>
    <div className='grid'>
      <h3 className='body-l-b m-b-xs'>Data specific for you target age group</h3>
      <div className='c-1-3'>
        <Stats
          header='Target age population'
          data={targetPopulation ? `${targetPopulation} million` : notAvailable }
        />
      </div>

      <div className='c-2-3'>
        <StatsGroup
          headerLeft='Female in your target group'
          dataLeft={female ? `${female} million`: '' }
          headerRight='Male in your target group'
          dataRight={female ? `${male} million`: '' }
          statPercentage={(female/targetPopulation)*100}
          hasStat={!!(female && female !== 0)}
        />
        <StatsGroup
          headerLeft='Living in urban areas'
          dataLeft={urban ? `${urban}%`: '' }
          headerRight='Living in rural areas'
          dataRight={urban ? `${rural}%`: '' }
          statPercentage={urban}
          hasStat={!!(urban && urban !== 0)}
        />
      </div>
    </div>
  </div>
))

Table.propTypes = {
  population: PropTypes.number.isRequired,
  cpi: PropTypes.string.isRequired,
  urban: PropTypes.number.isRequired,
  rural: PropTypes.number.isRequired,
  female: PropTypes.number.isRequired,
  male: PropTypes.number.isRequired,
  internetPercentage: PropTypes.number.isRequired,
  internetTotal: PropTypes.number.isRequired,
  targetPopulation: PropTypes.number.isRequired,
  languages: PropTypes.string.isRequired
}
