import React, { memo, useState } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'
import Slider from 'react-slick'

const CaseStudy = memo(({ content: { heading, company, blocks } }) => {
  const [isOpen, setIsOpen] = useState(false)

  const toggleCaseStudy = () => {
    setIsOpen(!isOpen)
    let dataLayer = window.dataLayer || []
    dataLayer.push({
      event: 'openCaseStudy',
      caseStudy: heading,
    })
  }

  const sliderSettings = {
    media: {
      dots: false,
      infinite: true,
      speed: 500,
      slidesToShow: 1,
      slidesToScroll: 1,
      arrows: false,
    },
    quote: {
      centerMode: true,
      centerPadding: '20px',
      dots: true,
      arrows: false,
      infinite: false,
      speed: 500,
      slidesToShow: 1,
      slidesToScroll: 1,
    },
  }

  const responsiveBlock = (block, settings) => {
    const content = ReactHtmlParser(block.content)
    return (
      <>
        {content && (
          <>
            {/* Desktop rendering with content displayed as a stack  */}
            <div className="case-study__media body-l">
              {content}
            </div>

            {/* Mobile rendering with content displayed within a carousel  */}
            <div className={'case-study__mobile body-l ' + block.type + '-block'}>
              <Slider {...settings}>
                {content}
              </Slider>
            </div>
          </>
        )}
      </>
    )
  }

  const renderMediaBlock = () => {
    const mediaBlock = blocks.find((block) => block.type === 'media')
    return responsiveBlock(mediaBlock, sliderSettings.media)
  }

  const image = renderMediaBlock()

  const body = blocks.map((block) => {
    return (
      <>
        {block.type === 'quote' && (
          responsiveBlock(block, sliderSettings.quote)
        )}
        {block.type === 'text' && (
          ReactHtmlParser(block.content)
        )}
      </>
    )
  })

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
            {image}
            {isOpen && (
              <>
                {body}
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
})

function createCaseStudy({ element, content }) {
  ReactDOM.render(<CaseStudy content={content} />, element)
}

export { CaseStudy, createCaseStudy }
