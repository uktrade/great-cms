import React, { useRef } from 'react'
import Slider from 'react-slick'
import './LearnIntroductionSlider.scss'

const LearnIntroduction = () => {
  const sliderRef = useRef(null);
  let currentSlide = 0;

  const handleClick = () => {
    if (currentSlide === 2) {
        window.location.assign('/learn/categories')
    } else {
        sliderRef.current.slickNext()
    }
  }

  const customPaging = i => (
    <span className="learn__carousel-nav-item"><a>Goto slide {i + 1}</a></span>
  )

  return (
    <>
      <Slider
        afterChange={index => { currentSlide = index}}
        dotsClass="learn__carousel-ul"
        arrows={false}
        customPaging={customPaging}
        dots
        focusOnSelect
        ref={sliderRef}
        slidesToScroll={1}
        slidesToShow={1}
        speed={500}
      >
        <div className="learn__carousel-slide">
          <img
            alt="Abstract illustration"
            className="learn__carousel-image c-full-l"
            height="250"
            src="/static/images/learn-introduction-slide-1.png"
          />
          <p className="learn__carousel--paragraph">
            We’ve created simple, bite sized lessons to make it easier for you to learn about the world of exporting.
          </p>
        </div>
        <div className="learn__carousel-slide">
          <img
            alt="Abstract illustration"
            className="learn__carousel-image c-full-l"
            height="250"
            src="/static/images/learn-introduction-slide-2.png"
          />
          <p className="learn__carousel--paragraph">
            Develop your skills in exporting with our interactive online training, that helps you create your export
            plan, as you learn.
          </p>
        </div>
        <div className="learn__carousel-slide">
          <img
            alt="Abstract illustration"
            className="learn__carousel-image c-full-l"
            height="250"
            src="/static/images/learn-introduction-slide-3.png"
          />
          <p className="learn__carousel--paragraph">
            Key topics include how to conduct market research, define your risks, how to get paid, find contacts,
            partners and deals, which currency to trade in and delivering your goods or services.
          </p>
        </div>
      </Slider>
      <button className="button" onClick={handleClick} type="button">
        Continue
      </button>
    </>
  )
}

export default LearnIntroduction
