import React, { memo, useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import Slider from 'react-slick'
import useUniqueId from '@src/components/hooks/useUniqueId'
import { analytics } from '@src/Helpers'

const CaseStudy = memo(({ content: { heading, company, blocks } }) => {
  const [isOpen, setIsOpen] = useState(false)
  const id = useUniqueId('case-study')

  let expandButton

  const toggleCaseStudy = () => {
    setIsOpen(!isOpen)
    expandButton.focus()
    analytics({
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
            <div className="case-study__media body-l">{content}</div>

            {/* Mobile rendering with content displayed within a carousel  */}
            <div className="case-study__mobile body-l">
              <Slider {...settings}>{content}</Slider>
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
  /* eslint-disable react/no-array-index-key */
  const body = blocks.map((block, index) => {
    return (
      <span key={`block-${index}`}>
        {block.type === 'quote' && responsiveBlock(block, sliderSettings.quote)}
        {block.type === 'text' && ReactHtmlParser(block.content)}
      </span>
    )
  })
  /* eslint-enable react/no-array-index-key */

  return (
    <>
      <div className="case-study p-t-xs p-b-s">
        <div className="case-study__content media-block m-t-s">
          <i className="fa fa-comment" aria-hidden="true" />
          <div>
            <h3 className="cast-study__lead_title  h-m m-b-xs p-0">
              {ReactHtmlParser(heading)}
            </h3>
            <span className="case-study__company text-blue-deep-60 h-s p-0">
              {ReactHtmlParser(company)}
            </span>
            {/* eslint-disable jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events */}
            <span onClick={toggleCaseStudy} style={{ cursor: 'pointer' }}>
              {image}
            </span>
            {/* eslint-enable jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events */}
            <button
              type="button"
              className="button button--small button--tertiary button--icon case-study__open m-t-xs"
              aria-controls={id}
              aria-expanded={isOpen}
              onClick={toggleCaseStudy}
              ref={(_expandButton) => {
                expandButton = _expandButton
              }}
            >
              <i
                className={`fas fa-chevron-${isOpen ? 'up' : 'down'}`}
              />
              {isOpen ? 'Collapse case study' : 'Expand case study'}
            </button>
            {isOpen && <span id={id}>{body}</span>}
          </div>
        </div>
      </div>
    </>
  )
})

CaseStudy.propTypes = {
  content: PropTypes.shape({
    heading: PropTypes.string,
    company: PropTypes.string,
    blocks: PropTypes.arrayOf(
      PropTypes.shape({
        type: PropTypes.string,
        content: PropTypes.string,
      })
    ),
  }).isRequired,
}

function createCaseStudy({ element, content }) {
  ReactDOM.render(<CaseStudy content={content} />, element)
}

export { CaseStudy, createCaseStudy }
