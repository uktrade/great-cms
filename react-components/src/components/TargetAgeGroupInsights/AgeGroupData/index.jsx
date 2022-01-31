import React, { memo } from 'react'
import { Stats } from '@src/components/Stats'
import { getEpMarket } from '@src/reducers'
import { useSelector } from 'react-redux'
import { notAvailable, StatsGroup } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues } from '@src/Helpers'

const formatNumber = (val) => (val ? millify(val) : notAvailable)

const formatPercentage = (val, total) =>
  val ? `${normaliseValues((100 * val) / total)}%` : notAvailable

export const AgeGroupData = memo(
  ({ selectedGroups, target, totalPopulation, targetfemale, targetmale, urban, rural }) => {
    const country = useSelector((state) => getEpMarket(state))
    const isFiltered = selectedGroups.length > 0 && target !== totalPopulation
    return (
      <>
        <h3 className="body-l-b m-t-xs m-b-xs">
          More details on {country.country_name}
        </h3>
        <div className="stat-group">
          <div className="grid">
            <div className="c-1-3">
              <Stats
                header={isFiltered ? 'Target age population' : 'Total population'}
                data={formatNumber(target)}
              />
            </div>

            <div className="c-2-3 flex-direction-column">
              <StatsGroup
                headerLeft={`Female${isFiltered ? ' in your target group' : ''}`}
                dataLeft={formatNumber(targetfemale)}
                headerRight={`Male${isFiltered ? ' in your target group' : ''}`}
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
  selectedGroups: PropTypes.arrayOf(PropTypes.string),
  urban: PropTypes.number,
  rural: PropTypes.number,
  targetfemale: PropTypes.number,
  targetmale: PropTypes.number,
  target: PropTypes.number,
  totalPopulation: PropTypes.number,
}

AgeGroupData.defaultProps = {
  selectedGroups: [],
  urban: null,
  rural: null,
  targetfemale: null,
  targetmale: null,
  target: null,
  totalPopulation: null,
}
