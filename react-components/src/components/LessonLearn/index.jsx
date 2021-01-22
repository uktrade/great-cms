import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const LessonLearn = memo(({ show, url, title, category, duration }) => (
  <a
    className={`text-white link m-b-xs width-full ${
      show ? 'inline-block' : 'hidden'
    }`}
    href={url}
    title={title}
  >
    <div className="card bg-blue-deep-80 text-white">
      <h4 className="text-white h-s m-t-0 p-t-0 m-b-xs">{title}</h4>
      <div className="body-m text-white grid">
        <dl className="c-1-3">
          <dt>Learning category</dt>
          <dd className="bold">{category}</dd>
        </dl>
        <dl className="c-1-3">
          <dt>Lesson length</dt>
          <dd className="bold">{duration} read</dd>
        </dl>
      </div>
    </div>
  </a>
))

LessonLearn.propTypes = {
  show: PropTypes.bool,
  url: PropTypes.string,
  title: PropTypes.string,
  category: PropTypes.string,
  duration: PropTypes.string,
}

LessonLearn.defaultProps = {
  show: false,
  url: '',
  title: '',
  category: '',
  duration: '',
}
