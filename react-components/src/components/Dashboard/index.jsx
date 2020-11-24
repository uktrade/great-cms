import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import { analytics } from '../../Helpers'

export const Dashboard = ({ sections }) => {
  const [modal, setModal] = useState(false)

  const openComingSoonModal = (e) => {
    setModal(true)
    // record click on disable section
    analytics({
      'event':'ctaFeature',
      'featureTitle':e.target.dataset.sectiontitle
    })
  }

  return (
    <>
      <ComingSoon
        onClick={() => setModal(false)}
        isOpen={modal}
      />
      {sections.map(({ title, url, disabled }) => (
        <div className='c-1-3' key={url}>
          <div className='bg-white m-b-s section-list__item'>
            {disabled ?
              <div className='w-full link section-list__disabled' role='button' onClick={openComingSoonModal} >
                <div className='bg-blue-deep-20'>
                  <span className='section-list__coming bg-blue-deep-80 text-white body-m p-xxs' data-sectiontitle={title}>Coming soon</span>
                  <img className='w-full p-h-s p-t-m p-b-s' src='/static/images/coming-soon.svg' alt={title}  data-sectiontitle={title}/>
                </div>
                <div className='p-v-s p-h-xs'>
                  <h3 className='h-xs text-blue-deep-80 p-0' data-sectiontitle={title}>{title}</h3>
                </div>
              </div> :
              <a className='w-full link' href={url} title={title}>
                <div className='bg-blue-deep-20'>
                  <img className='w-full p-h-s p-t-m p-b-s' src='/static/images/ep-placeholder.svg' alt={title} />
                </div>
                <div className='p-v-s p-h-xs'>
                  <h3 className='h-xs text-blue-deep-80 p-0'>{title}</h3>
                </div>
              </a>
            }
          </div>
        </div>
      ))}
    </>
  )
}

Dashboard.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string,
      url: PropTypes.string,
      disabled: PropTypes.bool
    })
  ).isRequired,
}

