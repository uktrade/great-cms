import React, { memo, useRef } from 'react'
import PropTypes from 'prop-types'

import { FormGroup } from '../FormGroup'

export const TextArea = memo(
  ({
    errors,
    label,
    disabled,
    id,
    placeholder,
    value,
    onChange,
    description,
    tooltip,
    example,
    hideLabel,
    lesson,
    className,
    formGroupClassName,
    name,
  }) => {
    const expandTextArea = (el) => {
      if (el) {
        el.style.overflow = 'hidden'
        el.style.height = 0 // This is so the scroll-height doen't get padded out by a larget min-height
        el.style.height = el.scrollHeight + 'px'
      }
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
        <textarea
          className={`form-control ${className}`}
          id={id}
          name={name || id}
          disabled={disabled}
          onChange={(e) => onChange({ [name || id]: e.target.value })}
          placeholder={placeholder}
          value={value}
          ref={(el) => expandTextArea(el)}
        />
      </FormGroup>
    )
  }
)

TextArea.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.objectOf(PropTypes.string),
  example: PropTypes.oneOfType([
    PropTypes.shape({
      buttonTitle: PropTypes.string,
      header: PropTypes.string,
      content: PropTypes.string,
    }),
    PropTypes.string,
  ]),
  hideLabel: PropTypes.bool,
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }),
  className: PropTypes.string,
  formGroupClassName: PropTypes.string,
  name: PropTypes.string,
}

TextArea.defaultProps = {
  errors: [],
  disabled: false,
  placeholder: '',
  value: '',
  description: '',
  tooltip: {},
  example: {},
  hideLabel: false,
  lesson: {},
  className: '',
  formGroupClassName: '',
  name: null,
}
