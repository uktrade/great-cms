import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'
import { createVideoTranscript } from '../VideoTranscript/VideoTranscript'
import Slider from 'react-slick'

const CaseStudy = ({ content: { heading, company, body, carouselItems, mobileContent } }) => {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const videoBlock = document.querySelector('.case-study .block-video')

    if (videoBlock) {
      videoBlock.appendChild(document.createElement('div'))

      createVideoTranscript({
        element: document.querySelector('.case-study .block-video > div'),
        source: document.querySelector('.case-study .block-video video source[transcript]')
      })
    }
  }, [isOpen])

  const toggleCaseStudy = () => {
    setIsOpen(!isOpen)
    let dataLayer = window.dataLayer || []
    dataLayer.push({
      event: 'openCaseStudy',
      caseStudy: heading
    })
  }

  const settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false
  }

  return (
    <>
      <div className="case-study p-t-m p-b-s">
        {isOpen && (
          <button className="case-study__close" onClick={toggleCaseStudy} autoFocus>
            <i className="fas fa-times"></i>
            <span className="visually-hidden">Close</span>
          </button>
        )}
        <div className="case-study__content media-block">
          <i className="fas fa-newspaper" />
          <div>
            <h3 className="h-m m-b-xs p-0">{heading}</h3>
            {isOpen && (
              <>
                <p className="case-study__company h-s p-0">{company}</p>
                <div className="case-study__mobile body-l">
                  <Slider {...settings}>{ReactHtmlParser(carouselItems)}</Slider>
                  {ReactHtmlParser(mobileContent)}
                </div>
                <div className="case-study__media body-l" dangerouslySetInnerHTML={{ __html: body }} />
              </>
            )}
          </div>
        </div>
        {!isOpen && (
          <button className="button button--small button--tertiary case-study__open" onClick={toggleCaseStudy}>
            Open case study
          </button>
        )}
      </div>
    </>
  )
}

function createCaseStudy({ element, content }) {
  ReactDOM.render(<CaseStudy content={content} />, element)
}

export { CaseStudy, createCaseStudy }
