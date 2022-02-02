import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { uniqueId } from '@src/Helpers'

import { Tooltip } from '@components/tooltip/Tooltip'
import { LessonLearn } from '@src/components/LessonLearn'

export const Learning = memo(({ tooltip, example, lesson, className }) => {
  const [showExample, setShowExample] = useState(false)
  const [showLesson, setShowLesson] = useState(false)
  const hasLesson = lesson && Object.keys(lesson).length > 0
  const hasExample = example && !!example.content
  const [learnId] = useState(uniqueId())
  const exampleId = `example-content-${learnId}`
  const lessonId = `lesson-content-${learnId}`

  return (
    <>
      {(hasExample || hasLesson || !!tooltip) && (
        <div className={`learning ${className}`}>
          <div className="learning__buttons">
            {hasExample && (
              <button
                className="button-example button button--small button--tiny-toggle m-r-xs m-b-xs"
                type="button"
                aria-controls={exampleId}
                aria-expanded={showExample}
                onClick={() => {
                  setShowExample(!showExample)
                  setShowLesson(false)
                }}
              >
                <i className={`fas fa-chevron-${showExample ? 'up' : 'down'} m-r-xxs`} />
                {example.buttonTitle ? example.buttonTitle : 'Example'}
              </button>
            )}
            {hasLesson && (
              <button
                className="button-lesson button button--small button--tiny-toggle m-r-xs m-b-xs"
                type="button"
                aria-controls={lessonId}
                aria-expanded={showLesson}
                onClick={() => {
                  setShowLesson(!showLesson)
                  setShowExample(false)
                }}
              >
                <i className={`fas fa-chevron-${showLesson ? 'up' : 'down'} m-r-xxs`} />
                Lesson
              </button>
            )}
            {tooltip && tooltip.content && (
              // eslint-disable-next-line react/jsx-props-no-spreading
              <Tooltip {...tooltip} className="inline-block m-b-xs m-r-xs" />
            )}
          </div>

          <div className="learning__content" aria-live="polite">
            {hasExample && (
              <div
                id={exampleId}
                className={`form-group-example bg-${
                  example.bgColour ? example.bgColour : 'blue-deep-10'
                } p-s m-b-xs radius ${showExample ? '' : 'hidden'}`}
              >
                <h3 className="body-l-b">
                  {example.header
                    ? example.header
                    : 'A fictional example to help you complete this section'}
                </h3>
                <div className="m-t-xxs body-l">
                  {ReactHtmlParser(example.content)}
                </div>
              </div>
            )}
            {hasLesson && (
              <LessonLearn
                /* eslint-disable-next-line react/jsx-props-no-spreading */
                {...lesson}
                show={showLesson}
                id={lessonId}
              />
            )}
          </div>
        </div>
      )}
    </>
  )
})

Learning.propTypes = {
  tooltip: PropTypes.shape({
    content: PropTypes.string.isRequired,
    title: PropTypes.string,
  }),
  example: PropTypes.oneOfType([
    PropTypes.shape({
      buttonTitle: PropTypes.string,
      header: PropTypes.string,
      content: PropTypes.string,
      bgColour: PropTypes.string,
    }),
    PropTypes.string,
  ]),
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }),
  className: PropTypes.string,
}

Learning.defaultProps = {
  tooltip: null,
  example: null,
  lesson: null,
  className: '',
}
