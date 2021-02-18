import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import ErrorList from '@src/components/ErrorList'
import { Learning } from '@src/components/Learning/Learning'

export const FormGroup = memo(
  ({
    children,
    errors,
    tooltip,
    id,
    label,
    description,
    example,
    hideLabel,
    lesson,
    formGroupClassName,
  }) => {
    return (
      <div
        className={`form-group ${
          errors.length > 0 ? 'form-group-error' : ''
        } ${formGroupClassName}`}
      >
        <label
          className={`form-label ${hideLabel ? 'visually-hidden' : ''}`}
          htmlFor={id}
        >
          {label}
        </label>

        {description && (
          <div className="text-blue-deep-80 p-t-xs p-b-xs">
            {ReactHtmlParser(description)}
          </div>
        )}

        <Learning tooltip={tooltip} example={example} lesson={lesson} />
        <ErrorList errors={errors} />
        {children}
      </div>
    )
  }
)

FormGroup.propTypes = {
  children: PropTypes.element.isRequired,
  errors: PropTypes.arrayOf(PropTypes.string),
  tooltip: PropTypes.shape({
    content: PropTypes.string,
    title: PropTypes.string,
  }),
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  formGroupClassName: PropTypes.string,
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

FormGroup.defaultProps = {
  errors: [],
  description: '',
  tooltip: {},
  example: {},
  hideLabel: false,
  lesson: {},
  formGroupClassName: '',
}
