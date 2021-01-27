import React, { memo } from 'react'
import PropTypes from 'prop-types'

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
    onChange,
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
  }) => (
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
      <div className="flex-center">
        {prepend && (
          <span className="bg-blue-deep-10 text-blue-deep-60 bold prepend">
            {prepend}
          </span>
        )}
        <input
          className={`form-control ${
            prepend ? 'form-control-prepend' : ''
          } ${className}`}
          id={id}
          type={type}
          name={id}
          disabled={disabled}
          onChange={(e) => onChange({ [id]: e.target.value })}
          placeholder={placeholder}
          value={value}
          readOnly={readOnly}
          tabIndex={tabIndex}
        />
      </div>
    </FormGroup>
  )
)

Input.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
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
  tooltip: '',
  example: {},
  readOnly: false,
  tabIndex: '',
  hideLabel: false,
  lesson: {},
  prepend: '',
  className: '',
  formGroupClassName: '',
}
