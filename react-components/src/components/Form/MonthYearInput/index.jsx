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

    const currentYear = new Date().getFullYear();

    const yearsOptions = [...Array(10)].map((element, index) => {
      const year = `${currentYear + index}`

      return {
        label: year,
        value: year
      }
    })

    return (
      <fieldset className={className}>
        <legend className='m-b-xs'>{label}</legend>
        <div className='inputgroup'>
          <div className='inputgroup__input inputgroup__input--month'>
            <Select
              label='Month'
              id={monthName}
              name={monthName}
              update={onChange}
              options={monthsOptions}
              selected={`${monthValue}`}
            />
          </div>
          <div className="inputgroup__input inputgroup__input--year">
            <Select
              label='Year'
              id={yearName}
              name={yearName}
              update={onChange}
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
}

MonthYearInput.defaultProps = {
  monthName: 'month',
  monthValue: null,
  yearName: 'year',
  yearValue: null,
  onChange: () => {
  },
  className: null,
}
