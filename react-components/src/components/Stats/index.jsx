/* eslint-disable import/prefer-default-export */
import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Stats = memo(({ header, data, children, className, descriptionClassName }) => (
  <div className={`statistic ${className}`}>
    {children}
    <dl>
      <dt className="statistic__caption">{header}</dt>
      <dd className={`statistic__figure h-xs p-b-0 p-t-xxs ${descriptionClassName}`}>{data}</dd>
    </dl>
  </div>
))

Stats.propTypes = {
  header: PropTypes.string.isRequired,
  data: PropTypes.string.isRequired,
  className: PropTypes.string,
  descriptionClassName: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),
}

Stats.defaultProps = {
  className: '',
  descriptionClassName: '',
  children: '',
}
