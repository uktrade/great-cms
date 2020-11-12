import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Stats = memo(({
  header,
  data,
  children
}) => (
  <div className='statistic'>
    {children}
    <dl>
      <dt className='statistic__caption'>{header}</dt>
      <dd className='statistic__figure h-xs p-b-0 p-t-xxs'>{data}</dd>
    </dl>
  </div>
))

Stats.propTypes = {
  header: PropTypes.string.isRequired,
  data: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.element
  ]),
}

Stats.defaultProps = {
  children: ''
}

