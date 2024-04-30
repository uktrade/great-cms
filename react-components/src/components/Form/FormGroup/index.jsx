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
    infoClassName,
    info,
    message,
  }) => {
    return (
      <div
        className={`form-group ${
          errors.length > 0 ? 'form-group-error' : ''
        } ${formGroupClassName}`}
      >
        {message ? <div className="g-panel body-m govuk-!-margin-top-2 govuk-!-margin-bottom-2">{message}</div> : null}
        <label
          className={`form-label ${hideLabel ? 'visually-hidden' : ''}`}
          htmlFor={id}
        >
          {label}
          {info && (
            <ExpandCollapse
              buttonClass="icon-only info fas fa-lg fa-info-circle govuk-!-padding-right-0 govuk-!-padding-left-0 govuk-!-margin-left-1 govuk-!-margin-top-1 govuk-!-margin-bottom-1"
              buttonBefore
            >
              <div className={infoClassName || "g-panel body-m govuk-!-margin-top-2 govuk-!-margin-bottom-2"}>{info}</div>
            </ExpandCollapse>
          )}
        </label>

        {description && (
          <div className={descriptionClassName || 'govuk-!-padding-bottom-3 govuk-!-padding-top-3'}>
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
