import React, { memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import ErrorList from '@src/components/ErrorList'
import { Learning } from '@src/components/Learning/Learning'
import ExpandCollapse from '@src/components/ProductFinder/ExpandCollapse'

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
    descriptionClassName,
    info,
    message,
  }) => {
    return (
      <div
        className={`form-group ${
          errors.length > 0 ? 'form-group-error' : ''
        } ${formGroupClassName}`}
      >
        {message ? <div className="g-panel body-m m-v-xs">{message}</div> : null}
        <label
          className={`form-label ${hideLabel ? 'visually-hidden' : ''}`}
          htmlFor={id}
        >
          {label}
          {info && (
            <ExpandCollapse
              buttonClass="icon-only info fas fa-lg fa-info-circle text-blue-deep-90 m-f-xxs p-v-4 p-h-0"
              buttonBefore
            >
              <div className="g-panel body-m m-v-xs">{info}</div>
            </ExpandCollapse>
          )}
        </label>

        {description && (
          <div className={descriptionClassName || 'text-blue-deep-80 p-t-xs p-b-xs'}>
            {ReactHtmlParser(description)}
          </div>
        )}

        <Learning
          tooltip={tooltip} example={example}
          lesson={lesson}
        />
        <ErrorList errors={errors} />
        {children}
      </div>
    )
  },
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
  descriptionClassName: PropTypes.string,
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
  info: PropTypes.string,
  message: PropTypes.string,
}

FormGroup.defaultProps = {
  errors: [],
  description: '',
  tooltip: null,
  example: null,
  hideLabel: false,
  lesson: null,
  formGroupClassName: '',
  descriptionClassName: '',
  info: '',
  message: '',
}
