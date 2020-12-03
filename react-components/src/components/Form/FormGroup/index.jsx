import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '../../EducationalMomentTooltip'
import ErrorList from '../../ErrorList'

export const FormGroup = memo(({
  children,
  errors,
  tooltip,
  id,
  label,
  description,
  example,
  hideLabel,
  lesson
}) => {

  const [ toggleExample, setToggleExample] = useState(false)
  const [ toggleLesson, setToggleLesson] = useState(false)
  const hasLesson = Object.keys(lesson).length > 0

  return (
    <div
      className={`form-group ${errors.length > 0 ? 'form-group-error' : ''}`}
    >
      <label className={`form-label ${hideLabel ? 'visually-hidden': ''}`} htmlFor={id}>{label}</label>
      { description && <div className='text-blue-deep-80 p-t-xs p-b-xs' dangerouslySetInnerHTML={{ __html: description }} /> }

      <div className='m-b-xs'>
        { example &&
        <button
          className='button-example button button--small button--tertiary m-r-xxs'
          type='button'
          onClick={() => {
            setToggleExample(!toggleExample)
            setToggleLesson(false)
          }}
        >
          <i className={`fas fa-chevron-${toggleExample ? 'up' : 'down'} m-r-xxs`} />Example
        </button>
        }
        { hasLesson &&
        <button
          className='button-lesson button button--small button--tertiary m-r-xxs'
          type='button'
          onClick={() => {
            setToggleLesson(!toggleLesson)
            setToggleExample(false)
          }}
        >
          <i className={`fas fa-chevron-${toggleLesson ? 'up' : 'down'} m-r-xxs`} />Lesson
        </button>
        }
        {
          tooltip &&
          <EducationalMomentTooltip
            heading=''
            description={tooltip}
            id={id}
            type='LEFT'
          />
        }
      </div>

      {
        example &&
        <dl className={`form-group-example bg-blue-deep-10 p-xs m-b-xs ${toggleExample ? '' : 'hidden'}`}>
          <dt className='body-l-b'>A fictional example to help you complete this section</dt>
          <dd className='m-t-xxs body-l' dangerouslySetInnerHTML={{ __html: example }} />
        </dl>
      }
      { hasLesson &&
        <a
          className={`text-white link m-b-xs ${toggleLesson ? 'inline-block' : 'hidden'}`}
          href={lesson.url}
          title={lesson.title}
        >
          <div className='card bg-blue-deep-80 text-white'>
            <h4 className='text-white h-s m-t-0 p-t-0 m-b-xs'>{lesson.title}</h4>
            <div className='body-m text-white grid'>
              <dl className='c-1-3'>
                <dt>Learning category</dt>
                <dd className='bold'>{lesson.category}</dd>
              </dl>
              <dl className='c-1-3'>
                <dt>Lesson length</dt>
                <dd className='bold'>{lesson.duration} read</dd>
              </dl>
            </div>
          </div>
        </a>
      }
      <ErrorList
        errors={errors}
      />
      {children}
    </div>
  )
})

FormGroup.propTypes = {
  children: PropTypes.element.isRequired,
  errors: PropTypes.arrayOf(PropTypes.string),
  tooltip: PropTypes.string,
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  example: PropTypes.string,
  hideLabel: PropTypes.bool,
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string
  }),
}

FormGroup.defaultProps = {
  errors: [],
  description: '',
  tooltip: '',
  example: '',
  hideLabel: false,
  lesson: {}
}
