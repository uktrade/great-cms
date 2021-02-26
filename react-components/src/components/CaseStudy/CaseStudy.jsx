import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'
import { createVideoTranscript } from '../VideoTranscript/VideoTranscript'
import Slider from 'react-slick'

const CaseStudy = ({ content: { heading, company, body, carouselItems, carouselQuotes } }) => {
  const [isOpen, setIsOpen] = useState(false)

  console.log(body)
  useEffect(() => {
    const videoBlock = document.querySelector('.case-study .block-video')

    if (videoBlock) {
      videoBlock.appendChild(document.createElement('div'))

      createVideoTranscript({
        element: document.querySelector('.case-study .block-video > div'),
        source: document.querySelector(
          '.case-study .block-video video source[transcript]'
        ),
      })
    }
  }, [isOpen])

  const toggleCaseStudy = () => {
    setIsOpen(!isOpen)
    let dataLayer = window.dataLayer || []
    dataLayer.push({
      event: 'openCaseStudy',
      caseStudy: heading,
    })
  }

  const settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
  }

  return (
    <>
      <div className="case-study p-t-m p-b-s">
        {isOpen && (
          <button
            className="case-study__close"
            onClick={toggleCaseStudy}
            autoFocus
          >
            <i className="fas fa-times"></i>
            <span className="visually-hidden">Close</span>
          </button>
        )}
        <div className="case-study__content media-block m-t-s">
          <i className="fa fa-comment" aria-hidden="true"></i>
          <div>
            <h3 className="cast-study__lead_title  h-m m-b-xs p-0">
              {heading}
            </h3>
            <span className="case-study__company text-blue-deep-60 h-s p-0">
              {company}
            </span>
            <div className="case-study__media m-t-n-xs m-b-s">
              <Slider {...settings}>{ReactHtmlParser(carouselItems)}</Slider>
            </div>
            <div className="case-study__quotes m-t-n-xs m-b-s">
              <Slider {...settings}>{ReactHtmlParser(carouselQuotes)}</Slider>
            </div>

            {isOpen && (
              <>
                <div className="case-study__media body-l">
                  {ReactHtmlParser(body)}
                </div>
                <div className="case-study__mobile body-l">
                  {ReactHtmlParser(body)}
                </div>
              </>
            )}
          </div>
        </div>
        {!isOpen && (
          <button
            className="button button--small button--tertiary case-study__open m-t-xs"
            onClick={toggleCaseStudy}
          >
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
