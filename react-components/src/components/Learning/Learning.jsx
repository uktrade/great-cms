import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import { Tooltip } from '@components/tooltip/Tooltip'
import { LessonLearn } from '@src/components/LessonLearn'

export const Learning = memo(({ tooltip, example, lesson, className }) => {
  const [toggleExample, setToggleExample] = useState(false)
  const [toggleLesson, setToggleLesson] = useState(false)
  const hasLesson = Object.keys(lesson).length > 0
  const hasExample = example.content
  const controlAreaId = `learning-content-area-${new Date().getTime()}`

  return (
    <>
      {!!(hasExample || hasLesson || tooltip) && (
        <div className={`learning ${className}`}>
          <div className="learning__buttons">
            {hasExample && (
              <button
                className="button-example button button--small button--tertiary button--icon m-r-xxs m-b-xs"
                type="button"
                aria-controls={controlAreaId}
                aria-expanded={toggleExample}
                onClick={() => {
                  setToggleExample(!toggleExample)
                  setToggleLesson(false)
                }}
              >
                <i
                  className={`fas fa-chevron-${
                    toggleExample ? 'up' : 'down'
                  }`}
                />
                {example.buttonTitle ? example.buttonTitle : 'Example'}
              </button>
            )}
            {hasLesson && (
              <button
                className="button-lesson button button--small button--tertiary button--icon m-r-xxs m-b-xs"
                type="button"
                aria-controls={controlAreaId}
                aria-expanded={toggleExample}
                onClick={() => {
                  setToggleLesson(!toggleLesson)
                  setToggleExample(false)
                }}
              >
                <i
                  className={`fas fa-chevron-${
                    toggleLesson ? 'up' : 'down'
                  }`}
                />
                Lesson
              </button>
            )}
            {tooltip.content && (
              <Tooltip {...tooltip} className="inline-block m-b-xs" />
            )}
          </div>
          <div className="learning__content" id={controlAreaId}>
            {hasExample && (
              <dl
                className={`form-group-example bg-${
                  example.bgColour ? example.bgColour : 'blue-deep-10'
                } p-s m-b-xs radius ${toggleExample ? '' : 'hidden'}`}
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
          </div>
        </div>
      )}
    </>
  )
})

Learning.propTypes = {
  tooltip: PropTypes.shape({
    content: PropTypes.string,
    title: PropTypes.string,
  }),
  example: PropTypes.shape({
    buttonTitle: PropTypes.string,
    header: PropTypes.string,
    content: PropTypes.string,
    bgColour: PropTypes.string,
  }),
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }),
  className: PropTypes.string,
}

Learning.defaultProps = {
  tooltip: {},
  example: {},
  lesson: {},
  className: '',
}
