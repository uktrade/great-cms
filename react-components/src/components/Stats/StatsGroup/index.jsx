import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const notAvailable = 'Data not available'

export const StatsGroup = memo(({
  headerLeft,
  headerRight,
  dataLeft,
  dataRight,
  statPercentage,
  hasStat
}) => (
  <div className='statistic'>
    <div className='statistic__group'>
      <dl>
        <dt className='statistic__caption p-t-xs'>{headerLeft}</dt>
        <dd className='statistic__figure h-xs p-b-0 p-t-s'>{dataLeft}</dd>
      </dl>
      <dl>
        <dt className='statistic__caption p-t-xs'>{headerRight}</dt>
        <dd className='statistic__figure h-xs p-b-0 p-t-s'>{dataRight}</dd>
      </dl>
      { hasStat &&
      <div className='statistic__percentage bg-red-80 radius m-b-xs'>
        <span className='bg-blue-deep-80 radius' style={{ width: `${statPercentage}%` }} />
      </div>
      }
    </div>
    {!hasStat && <span className='h-xs p-t-0'>{notAvailable}</span>}
  </div>
))

StatsGroup.propTypes = {
  headerLeft: PropTypes.string.isRequired,
  headerRight: PropTypes.string.isRequired,
  dataLeft: PropTypes.string.isRequired,
  dataRight: PropTypes.string.isRequired,
  statPercentage: PropTypes.number.isRequired,
  hasStat: PropTypes.bool.isRequired,
}
