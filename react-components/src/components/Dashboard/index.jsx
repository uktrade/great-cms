import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import { analytics } from '@src/Helpers'

export const Dashboard = memo(
  ({ sections, exportPlanProgress: { section_progress } }) => {
    const [modal, setModal] = useState(false)
    const openComingSoonModal = (e) => {
      setModal(true)
      // record click on disable section
      analytics({
        event: 'ctaFeature',
        featureTitle: e.target.dataset.sectiontitle,
      })
    }

    return (
      <>
        <ComingSoon onClick={() => setModal(false)} isOpen={modal} />
        {sections.map(({ title, url, disabled, is_complete, image }, i) => (
          <div className="c-1-3-xl c-1-2-m" key={url}>
            <div
              className={`bg-white m-b-s section-list__item ${
                is_complete ? 'section-list__item--is-complete' : ''
              }`}
            >
              {disabled ? (
                <div
                  className="width-full link section-list__disabled section-list__link"
                  onClick={openComingSoonModal}
                  aria-hidden="true"
                  role="button"
                >
                  <div className="section-list__image-container">
                    <span
                      className="section-list__coming bg-blue-deep-80 text-white body-m p-xxs"
                      data-sectiontitle={title}
                    >
                      Coming soon
                    </span>
                    <img
                      className="width-full p-h-s p-t-m p-b-s"
                      src="/static/images/coming-soon.svg"
                      alt=""
                      data-sectiontitle={title}
                    />
                  </div>
                  <div className="p-v-s p-h-xs">
                    <h3
                      className="h-xs text-blue-deep-80 p-0"
                      data-sectiontitle={title}
                    >
                      {title}
                    </h3>
                  </div>
                </div>
              ) : (
                <a
                  className="width-full link section-list__link"
                  href={url}
                  title={title}
                >
                  <div
                    className="section-list__image-container"
                    data-complete={is_complete ? 'Complete' : ''}
                  >
                    {is_complete && <span className="visually-hidden">Complete</span>}
                    <img
                      className={`width-full p-h-s p-t-m p-b-s ${
                        is_complete ? 'bg-green-30' : 'bg-blue-deep-20'
                      }`}
                      src={`/static/images/${image}`}
                      alt=""
                    />
                  </div>
                  <div className="p-xs">
                    <h3 className="h-xs text-blue-deep-80 p-0">{title}</h3>
                    <p className="m-b-0 m-t-xxs">
                      {section_progress.find((x) => x.url === url).populated}{' '}
                      out of {section_progress.find((x) => x.url === url).total}{' '}
                      questions answered
                    </p>
                  </div>
                </a>
              )}
            </div>
          </div>
        ))}
      </>
    )
  }
)

Dashboard.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string,
      url: PropTypes.string,
      disabled: PropTypes.bool,
      is_complete: PropTypes.bool,
      completed: PropTypes.string,
      total: PropTypes.string,
      image: PropTypes.string,
    })
  ).isRequired,
  exportPlanProgress: PropTypes.shape({
    section_progress: PropTypes.arrayOf(
      PropTypes.shape({
        populated: PropTypes.number,
        total: PropTypes.number,
        url: PropTypes.string,
      })
    ),
  }).isRequired,
}
