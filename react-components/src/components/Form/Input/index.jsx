import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { dateFormat, validation } from '@src/Helpers'
import { FormGroup } from '../FormGroup'

export const Input = memo(
  ({
    errors,
    label,
    id,
    type,
    value,
    onChange: update,
    description,
    tooltip,
    example,
    hideLabel,
    lesson,
    prepend,
    className,
    formGroupClassName,
    minDate,
    maxDate,
    decimal,
    ...inputAttributes
  }) => {
    const IsValidNumber = (e, rule = decimal) => {
      const t = parseInt(e.key, 10)
      const isInteger = Number.isInteger(t)
      const validateNumber =
        rule === 2
          ? isInteger && !validation.twoDecimal(value + t)
          : (isInteger || e.key === '.') && !validation.wholeNumber(value + t)

      if (type === 'number') {
        if (validation.onlyOneZero(t, value)) {
          e.preventDefault()
        } else if (validateNumber) {
          e.preventDefault()
        }
      }
    }

    const onChange = (e) => {
      let { value: updatedValue } = e.target
      if (type === 'number' && !updatedValue) {
        updatedValue = null
      }
      update({ [id]: updatedValue })
    }

    return (
      <FormGroup
        errors={errors}
        label={label}
        description={description}
        tooltip={tooltip}
        example={example}
        id={id}
        hideLabel={hideLabel}
        lesson={lesson}
        formGroupClassName={formGroupClassName}
      >
        <div className={`flex-center ${type === 'date' ? 'select-date' : ''}`}>
          {prepend && (
            <span className="bg-blue-deep-10 text-blue-deep-60 bold prepend">
              {prepend}
            </span>
          )}
          {type === 'date' && (
            <span className="select-date__friendly">{dateFormat(value)}</span>
          )}
          <input
            className={`form-control ${
              prepend ? 'form-control-prepend' : ''
            } ${className}`}
            id={id}
            type={type}
            min={minDate}
            max={maxDate}
            name={id}
            onChange={onChange}
            onKeyDown={IsValidNumber}
            value={value}
            {...inputAttributes} // eslint-disable-line react/jsx-props-no-spreading
          />
        </div>
      </FormGroup>
    )
  }
)

Input.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  minDate: PropTypes.string,
  maxDate: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.objectOf(PropTypes.string),
  example: PropTypes.shape({
    buttonTitle: PropTypes.string,
    header: PropTypes.string,
    content: PropTypes.string,
  }),
  hideLabel: PropTypes.bool,
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }),
  prepend: PropTypes.string,
  className: PropTypes.string,
  formGroupClassName: PropTypes.string,
  decimal: PropTypes.oneOf([2, 0]),
}

Input.defaultProps = {
  errors: [],
  type: 'text',
  value: '',
  description: '',
  tooltip: {},
  example: {},
  hideLabel: false,
  lesson: {},
  prepend: '',
  className: '',
  formGroupClassName: '',
  minDate: '',
  maxDate: '',
  decimal: 2,
}
