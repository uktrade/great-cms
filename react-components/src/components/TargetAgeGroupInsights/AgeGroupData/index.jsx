import React, { memo } from 'react'
import { Stats } from '@src/components/Stats'
import { notAvailable, StatsGroup } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues } from '@src/Helpers'

const formatNumber = (val) => val ? millify(val*1000) : notAvailable

const formatPercentage = (val, total) => val ? `${normaliseValues(100*val/total)}%` : notAvailable

export const AgeGroupData = memo(
  ({ targetPopulation, female, male, urban, rural }) => (
    <>
      <h3 className="body-l-b m-t-s m-b-xs">
        Data specific for your target age group
      </h3>
      <div className="stat-group radius-top-xs">
        <div className="grid">
          <div className="c-1-3">
            <Stats
              header="Target age population"
              data={formatNumber(targetPopulation)}
            />
          </div>

          <div className="c-2-3 flex-direction-column">
            <StatsGroup
              headerLeft="Female in your target group"
              dataLeft={formatNumber(female)}
              headerRight="Male in your target group"
              dataRight={formatNumber(male)}
              statPercentage={(female / targetPopulation) * 100}
              hasStat={!!(female && female !== 0)}
              className="stat-group--cols stat-group--percentage"
            />
            <StatsGroup
              headerLeft="Living in urban areas"
              dataLeft={formatPercentage(rural, rural+urban)}
              headerRight="Living in rural areas"
              dataRight={formatPercentage(urban, rural+urban)}
              statPercentage={rural / (urban+rural)*100}
              hasStat={!!(urban && urban !== 0)}
              className="stat-group--cols stat-group--percentage"
            />
          </div>
        </div>
      </div>
    </>
  )
)

AgeGroupData.propTypes = {
  urban: PropTypes.number,
  rural: PropTypes.number,
  female: PropTypes.number,
  male: PropTypes.number,
  targetPopulation: PropTypes.number,
}

AgeGroupData.defaultProps = {
  urban: '',
  rural: '',
  female: '',
  male: '',
  targetPopulation: '',
}
