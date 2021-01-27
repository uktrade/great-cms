import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import { Tooltip } from '@components/tooltip/Tooltip'
import ErrorList from '@src/components//ErrorList'
import { LessonLearn } from '@src/components/LessonLearn'

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
    className,
    formGroupClassName,
  }) => {
    const [toggleExample, setToggleExample] = useState(false)
    const [toggleLesson, setToggleLesson] = useState(false)
    const hasLesson = Object.keys(lesson).length > 0
    const hasExample = example.content
    return (
      <div
        className={`form-group ${
          errors.length > 0 ? 'form-group-error' : ''
        } ${className} ${formGroupClassName}`}
      >
        {label && (
          <label
            className={`form-label ${hideLabel ? 'visually-hidden' : ''}`}
            htmlFor={id}
          >
            {label}
          </label>
        )}
        {description && (
          <div className="text-blue-deep-80 p-t-xs p-b-xs">
            {ReactHtmlParser(description)}
          </div>
        )}

        {!!(hasExample || hasLesson || tooltip) && (
          <div className="m-b-xs">
            {hasExample && (
              <button
                className="button-example button button--small button--tertiary m-r-xxs"
                type="button"
                onClick={() => {
                  setToggleExample(!toggleExample)
                  setToggleLesson(false)
                }}
              >
                <i
                  className={`fas fa-chevron-${
                    toggleExample ? 'up' : 'down'
                  } m-r-xxs`}
                />
                {example.buttonTitle ? example.buttonTitle : 'Example'}
              </button>
            )}
            {hasLesson && (
              <button
                className="button-lesson button button--small button--tertiary m-r-xxs"
                type="button"
                onClick={() => {
                  setToggleLesson(!toggleLesson)
                  setToggleExample(false)
                }}
              >
                <i
                  className={`fas fa-chevron-${
                    toggleLesson ? 'up' : 'down'
                  } m-r-xxs`}
                />
                Lesson
              </button>
            )}
            {tooltip && <Tooltip content={tooltip} className="inline-block" />}
          </div>
        )}

        {hasExample && (
          <dl
            className={`form-group-example bg-blue-deep-10 p-xs m-b-xs ${
              toggleExample ? '' : 'hidden'
            }`}
          >
            <dt className="body-l-b">
              {example.header
                ? example.header
                : 'A fictional example to help you complete this section'}
            </dt>
            <dd className="m-t-xxs body-l">
              {ReactHtmlParser(example.content)}
            </dd>
          </dl>
        )}
        {hasLesson && <LessonLearn {...lesson} show={toggleLesson} />}
        <ErrorList errors={errors} />
        {children}
      </div>
    )
  }
)

FormGroup.propTypes = {
  children: PropTypes.element.isRequired,
  errors: PropTypes.arrayOf(PropTypes.string),
  tooltip: PropTypes.string,
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  className: PropTypes.string,
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
  tooltip: '',
  example: {},
  hideLabel: false,
  lesson: {},
  className: '',
  formGroupClassName: '',
}
