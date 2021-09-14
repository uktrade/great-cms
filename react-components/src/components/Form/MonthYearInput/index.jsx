import React, { memo, useState } from 'react'
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

    const [showError, setShowError] = useState(false)

    const monthsOptions = MONTHS.map((month, i) => ({
      label: month,
      value: `${i + 1}`,
    }))

    const handleOnChange = (item) => {
      onChange(item)

      if(!minYear || !minMonth || (item[yearName] && item[yearName] < 1000)){
        onChange(item)
        return
      }

      const startDate = new Date(minYear, minMonth - 1);
      const completeYear = item[yearName] ? item[yearName] : yearValue;
      const completeMonth = item[monthName] ? item[monthName] : monthValue;
      const completeDate = new Date(completeYear, completeMonth - 1);

      if(completeDate >= startDate) {
        setShowError(false)

      } else {
        setShowError(true)
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

        {showError && <div className="inputgroup__error">
          "Complete by" date cannot procede "Start objective in" date
        </div>}
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
