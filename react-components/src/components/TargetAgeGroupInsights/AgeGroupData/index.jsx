import React, { memo } from 'react'
import { Stats } from '@src/components/Stats'
import { getMarkets } from '@src/reducers'
import { useSelector } from 'react-redux'
import { notAvailable, StatsGroup } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues } from '@src/Helpers'

const formatNumber = (val) => (val ? millify(val) : notAvailable)

const formatPercentage = (val, total) =>
  val ? `${normaliseValues((100 * val) / total)}%` : notAvailable

export const AgeGroupData = memo(
  ({ target, targetfemale, targetmale, urban, rural }) => {
    const country = useSelector((state) => getMarkets(state))
    return (
      <>
        <h3 className="body-l-b m-t-xs m-b-xs">
          More details on {country.country_name}
        </h3>
        <div className="stat-group">
          <div className="grid">
            <div className="c-1-3">
              <Stats
                header="Target age population"
                data={formatNumber(target)}
              />
            </div>

            <div className="c-2-3 flex-direction-column">
              <StatsGroup
                headerLeft="Female in your target group"
                dataLeft={formatNumber(targetfemale)}
                headerRight="Male in your target group"
                dataRight={formatNumber(targetmale)}
                statPercentage={(targetfemale / target) * 100}
                hasStat={!!(targetfemale && targetfemale !== 0)}
                className="stat-group--cols stat-group--percentage"
              />
              <StatsGroup
                headerLeft="Living in rural areas"
                dataLeft={formatPercentage(rural, rural + urban)}
                headerRight="Living in urban areas"
                dataRight={formatPercentage(urban, rural + urban)}
                statPercentage={(rural / (urban + rural)) * 100}
                hasStat={!!(urban && urban !== 0)}
                className="stat-group--cols stat-group--percentage"
              />
            </div>
          </div>
        </div>
      </>
    )
  }
)

AgeGroupData.propTypes = {
  urban: PropTypes.number,
  rural: PropTypes.number,
  female: PropTypes.number,
  male: PropTypes.number,
  targetPopulation: PropTypes.number,
}

AgeGroupData.defaultProps = {
  urban: null,
  rural: null,
  female: null,
  male: null,
  targetPopulation: null,
}
