import React, { memo } from 'react'
import * as PropTypes from 'prop-types'

import { Input } from '../Input'
import { Select } from '../Select'

export const MonthYearInput = memo(
  ({
     label,
     monthName = 'month',
     monthValue,
     yearName = 'year',
     yearValue,
     onChange,
     className,
     onChangeCombineFields,
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

    const monthsOptions = MONTHS.map((month, i) => ({
      label: month,
      value: `${i + 1}`,
    }))

    const handleChange = field => {
      if (!onChangeCombineFields) {
        return onChange(field)
      }

      const updateKey = Object.keys(field)[0] === monthName ? 'month' : 'year'
      const value = {
        month: monthValue || null,
        year: yearValue || null,
        [updateKey]: Object.values(field)[0],
      }
      return onChange(field, value)
    }

    return (
      <fieldset className={className}>
        <legend className="m-b-xs">{label}</legend>
        <div className="inputgroup">
          <div className="inputgroup__input inputgroup__input--month">
            <Select
              label="Month"
              id={monthName}
              name={monthName}
              update={handleChange}
              options={monthsOptions}
              selected={`${monthValue}`}
            />
          </div>
          <div className="inputgroup__input inputgroup__input--year">
            <Input
              label='Year'
              id={yearName}
              type='number'
              value={`${yearValue || ''}`}
              onChange={handleChange}
              size={4}
              inputMode='numeric'
              pattern='[0-9]*'
            />
          </div>
        </div>
      </fieldset>
    )
  }
)

MonthYearInput.propTypes = {
  label: PropTypes.string.isRequired,
  monthName: PropTypes.string,
  monthValue: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  yearName: PropTypes.string,
  yearValue: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
  className: PropTypes.string,
  onChangeCombineFields: PropTypes.bool,
}

MonthYearInput.defaultProps = {
  monthName: 'month',
  monthValue: null,
  yearName: 'year',
  yearValue: null,
  onChange: () => {
  },
  className: null,
  onChangeCombineFields: false,
}
