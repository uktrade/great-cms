import React, { memo, useEffect, useState } from 'react'
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
     minMonth,
     minYear,
     maxMonth,
     maxYear,
     setShowError
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

    useEffect(() => handleShowError({}), [])

    const handleOnChange = (item) => {
      onChange(item)
      handleShowError(item)
    }

    const handleShowError = (item) => {
      const selectedYear = item[yearName] ? item[yearName] : yearValue;
      const selectedMonth = item[monthName] ? item[monthName] : monthValue;
      const selectedDate = new Date(selectedYear, selectedMonth - 1);

      if(maxYear && maxMonth){
        const endDate = new Date(maxYear, maxMonth - 1);
        setShowError(selectedDate > endDate)
      }

      if(minYear && minMonth){
        const startDate = new Date(minYear, minMonth - 1);
        setShowError(selectedDate < startDate)
      }
    }

    return (
      <fieldset className={className}>
        <legend className='m-b-xs'>{label}</legend>
        <div className='inputgroup'>
          <div className='inputgroup__input inputgroup__input--month'>
            <Select
              label='Month'
              id={monthName}
              name={monthName}
              update={handleOnChange}
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
              onChange={handleOnChange}
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
  minMonth:  PropTypes.string,
  minYear:  PropTypes.string,
  maxMonth:  PropTypes.string,
  maxYear:  PropTypes.string,
  setShowError: PropTypes.func
}

MonthYearInput.defaultProps = {
  monthName: 'month',
  monthValue: null,
  yearName: 'year',
  yearValue: null,
  onChange: () => {
  },
  setShowError: () => {
  },
  className: null,
}
