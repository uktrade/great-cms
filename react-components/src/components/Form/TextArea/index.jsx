import React, { memo } from 'react'
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
    estimate,
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
      estimate={estimate}
    >
      <textarea
        className="form-control"
        id={id}
        name={id}
        disabled={disabled}
        onChange={(e) => onChange({ [id]: e.target.value })}
        placeholder={placeholder}
        value={value}
      />
    </FormGroup>
  )
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
  tooltip: PropTypes.string,
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
}

TextArea.defaultProps = {
  errors: [],
  disabled: false,
  placeholder: '',
  value: '',
  description: '',
  tooltip: '',
  example: {},
  hideLabel: false,
  lesson: {},
}
