import React, { memo, useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import Slider from 'react-slick'
import useUniqueId from '@src/components/hooks/useUniqueId'
import { analytics } from '@src/Helpers'

const CaseStudy = memo(({ content: { heading, company, blocks } }) => {

  const id = useUniqueId('case-study')

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
      <div className="case-study govuk-!-padding-top-3 govuk-!-padding-bottom-4">
        <div className="case-study__content media-block govuk-!-margin-top-4">
          <div>
            <h2 className="govuk-heading-l cast-study__lead_title govuk-heading-m govuk-!-margin-bottom-3 govuk-!-padding-0">
              {ReactHtmlParser(heading)}
            </h2>
            <h3 className="case-study__company govuk-heading-m govuk-!-padding-0">
              {ReactHtmlParser(company)}
            </h3>
            {/* eslint-disable jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events */}
            {image}
            {/* eslint-enable jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events */}
            <details class="govuk-details govuk-!-margin-top-4" data-module="govuk-details">
              <summary class="govuk-details__summary">
                <span class="govuk-details__summary-text">
                  Show case study details
                </span>
              </summary>
              <div class="govuk-details__text">
                <span id={id}>{body}</span>
              </div>
          </details>
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
