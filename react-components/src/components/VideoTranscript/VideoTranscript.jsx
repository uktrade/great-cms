import React, { useState } from 'react'
import ReactDOM from 'react-dom'

const VideoTranscript = ({ transcript }) => {
  const [isOpen, setIsOpen] = useState(false)
  const iconClasses = isOpen ? 'fas fa-caret-down m-r-xs' : 'fas fa-caret-right m-r-xs'

  return transcript ? (
    <div className="video-transcript">
      <button className="link link--icon m-t-xs" onClick={() => setIsOpen(!isOpen)}>
        <i className={iconClasses}></i> <span className="link--underline">View transcript</span>
      </button>
      {isOpen && <div className="video-transcript__text-area m-t-xs">{transcript}</div>}
    </div>
  ) : null
}

function createVideoTranscript({ element, source }) {
  ReactDOM.render(<VideoTranscript transcript={source ? source.getAttribute('transcript') : null} />, element)
}

export { VideoTranscript, createVideoTranscript }
