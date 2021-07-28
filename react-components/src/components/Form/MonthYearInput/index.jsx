import React, { memo } from 'react'
import * as PropTypes from 'prop-types'

import { Input } from '../Input'
import { Select } from '../Select'

export const MonthYearInput = memo(
  ({
    label,
    month_name = 'month',
    month_value,
    year_name = 'year',
    year_value,
    onChange,
    className,
  }) => {
    const MONTHS = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ]

    const monthsOptions = MONTHS.map((label, i) => ({
      label,
      value: `${i + 1}`,
    }))

    return (
      <fieldset className={className}>
        <legend className="m-b-xs">{label}</legend>
        <div className="inputgroup">
          <div className="inputgroup__input inputgroup__input--month">
            <Select
              label="Month"
              id={month_name}
              name={month_name}
              update={onChange}
              options={monthsOptions}
              selected={`${month_value}`}
            />
          </div>
          <div className="inputgroup__input inputgroup__input--year">
            <Input
              label="Year"
              id={year_name}
              type="number"
              value={`${year_value || ''}`}
              onChange={onChange}
              size={4}
              pattern="[0-9]*"
            />
          </div>
        </div>
      </fieldset>
    )
  }
)

MonthYearInput.propTypes = {
  label: PropTypes.string,
  month_name: PropTypes.string,
  month_value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  year_name: PropTypes.string,
  year_value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
  className: PropTypes.string,
}
