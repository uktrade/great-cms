import React, { memo } from 'react'
import * as PropTypes from 'prop-types'

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

    const handleChange = (field) => {
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

    const yearsOptions = [...Array(10)].map((element, index) => {
      const year = `${new Date().getFullYear() + index}`

      return {
        label: year,
        value: year,
      }
    })

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
            <Select
              label="Year"
              id={yearName}
              name={yearName}
              update={handleChange}
              options={yearsOptions}
              selected={`${yearValue}`}
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
  onChange: () => {},
  className: null,
  onChangeCombineFields: false,
}
