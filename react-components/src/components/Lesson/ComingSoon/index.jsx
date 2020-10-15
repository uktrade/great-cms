import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ title, lessons = [] }) => {
  const [modal, setModal] = useState(false)
  return (
    <>
      <ReactModal
        isOpen={modal}
        className="ReactModal__Content ReactModalCentreScreen"
        overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
        contentLabel="Modal"
      >
        <Modal
          backUrl="/export-plan/dashboard/"
          header="This Lesson is coming soon"
          content="This feature is not available in Beta version of the new great.gov.uk platform."
          onClick={() => setModal(false)}
          buttonText="Ok"
        />
      </ReactModal>
      <div className="learn__topic-item-details c-1-3-l">
        <h2 className="learn__topic-item-title h-m p-t-0">{title}</h2>
      </div>
      <ul className="learn__lessons-list c-2-3-l">
        {lessons.map((lesson) => (
          <li className={`learn__lesson-item ${lesson.isPlaceholder ? 'learn__lesson-item--placeholder' : ''}`}>
            <a
              href={lesson.url}
              className="learn__lesson-item-link h-xs"
              onClick={(e) => {
                if (lesson.isPlaceholder) {
                  e.preventDefault()
                  setModal(true)
                }
              }}
            >
              <span>{lesson.title}</span>
              {lesson.isPlaceholder && <button className="button button--secondary button--small">Coming soon</button>}
            </a>
          </li>
        ))}
      </ul>
    </>
  )
}

function createComingSoonModal({ element, title, lessons }) {
  ReactDOM.render(<ComingSoon title={title} lessons={lessons} />, element)
}

export { createComingSoonModal }
