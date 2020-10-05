import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { VideoTranscript } from '../VideoTranscript/VideoTranscript'

const CaseStudy = ({ content: { heading, company, body } }) => {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <div className="case-study m-b-l">
      {isOpen && (
        <button className="case-study__close" onClick={() => setIsOpen(false)}>
          <i className="fas fa-times"></i>
          <span className="visually-hidden">Close</span>
        </button>
      )}
      <div className="media-block">
        <i class="fas fa-newspaper" />
        <div>
          <h3 className="h-m m-b-xs p-0">{heading}</h3>
          {isOpen && (
            <>
              <p className="case-study__company h-s p-0">{company}</p>
              <div className="case-study__media">
                <img src="https://dummyimage.com/600x300/000/fff" alt="" />
                <img src="https://dummyimage.com/600x300/000/fff" alt="" />
                <video>
                  <source
                    src="https://paas-s3-broker-prod-lon-36184474-09f3-424b-9e27-f0ac51d7da9b.s3.amazonaws.com/media/Signpost_video_4_-_Edit_II_2_TybPk2P.mp4"
                    type="video/mp4"
                  ></source>
                </video>
                <VideoTranscript transcript="abc" />
              </div>
            </>
          )}
        </div>
      </div>
      {!isOpen && (
        <button className="button button--small button--tertiary" onClick={() => setIsOpen(true)}>
          Open case study
        </button>
      )}
      {isOpen && <div className="body-l m-t-s">{body}</div>}
    </div>
  )
}

function createCaseStudy({ element, content }) {
  ReactDOM.render(<CaseStudy content={content} />, element)
}

export { CaseStudy, createCaseStudy }
