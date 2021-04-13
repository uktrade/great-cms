import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { dateFormat, validation } from '@src/Helpers'
import { FormGroup } from '../FormGroup'

export const Input = memo(
  ({
    errors,
    label,
    disabled,
    id,
    type,
    placeholder,
    value,
    onChange: update,
    description,
    tooltip,
    example,
    readOnly,
    tabIndex,
    hideLabel,
    lesson,
    prepend,
    className,
    formGroupClassName,
    minDate,
  }) => {
    const IsValidNumber = (e) => {
      const t = parseInt(e.key, 10)

      if (type === 'number') {
        if (t === 0 && value.length === 1) {
          e.preventDefault()
        } else if (Number.isInteger(t) && !validation.twoDecimal(value + t)) {
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
            name={id}
            disabled={disabled}
            onChange={onChange}
            onKeyDown={IsValidNumber}
            placeholder={placeholder}
            value={value}
            readOnly={readOnly}
            tabIndex={tabIndex}
          />
        </div>
      </FormGroup>
    )
  }
)

Input.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  minDate: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.objectOf(PropTypes.string),
  example: PropTypes.shape({
    buttonTitle: PropTypes.string,
    header: PropTypes.string,
    content: PropTypes.string,
  }),
  readOnly: PropTypes.bool,
  tabIndex: PropTypes.string,
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
}

Input.defaultProps = {
  errors: [],
  disabled: false,
  type: 'text',
  placeholder: '',
  value: '',
  description: '',
  tooltip: {},
  example: {},
  readOnly: false,
  tabIndex: '',
  hideLabel: false,
  lesson: {},
  prepend: '',
  className: '',
  formGroupClassName: '',
  minDate: '',
}
