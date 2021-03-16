import React, { memo } from 'react'
import ReactHtmlParser from 'react-html-parser'
import PropTypes from 'prop-types'

export const Stats = memo(
  ({
    header,
    data,
    children,
    className,
    descriptionClassName,
    childPosition,
  }) => (
    <div className={`statistic ${className}`}>
      {childPosition === 'top' ? children : ''}
      <dl>
        <dt className="statistic__caption">{header}</dt>
        <dd
          className={`statistic__figure h-xs p-b-0 p-t-xxs ${descriptionClassName}`}
        >
          {ReactHtmlParser(data)}
        </dd>
      </dl>
      {childPosition === 'bottom' ? children : ''}
    </div>
  )
)

Stats.propTypes = {
  header: PropTypes.string.isRequired,
  data: PropTypes.string.isRequired,
  className: PropTypes.string,
  descriptionClassName: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),
  childPosition: PropTypes.string,
}

Stats.defaultProps = {
  className: '',
  descriptionClassName: '',
  children: '',
  childPosition: 'top',
}
