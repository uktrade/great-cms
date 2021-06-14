import React, { useState, memo, useCallback, useEffect } from 'react'
import PropTypes from 'prop-types'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import { analytics } from '@src/Helpers'
import DashboardSection from './DashboardSection'

export const Dashboard = memo(
  ({ sections, exportPlanProgress: { section_progress } }) => {
    const [modal, setModal] = useState(false)
    const [sectionActive, setSectionActive] = useState(0)
    const [activeUrl, setActiveUrl] = useState('')
    const [sectionLength, setSectionLength] = useState(sections.length - 1)

    const openComingSoonModal = (e) => {
      setModal(true)
      // record click on disable section
      analytics({
        event: 'ctaFeature',
        featureTitle: e.target.dataset.sectiontitle,
      })
    }

    // Handing user input.
    const handleUserKeyPress = useCallback(
      (event) => {
        const { keyCode } = event
        if (keyCode === 37) {
          if (sectionActive <= 0) {
            return
          }
          setSectionActive(sectionActive - 1)
        } else if (keyCode === 39) {
          if (sectionActive >= sectionLength) {
            return
          }
          setSectionActive(sectionActive + 1)
        } else if (keyCode === 13) {
          window.open(activeUrl, '_self')
        }
      },
      [sectionActive, activeUrl]
    )

    // Mount and dismout eventListener.
    useEffect(() => {
      window.addEventListener('keydown', handleUserKeyPress)
      return () => {
        window.removeEventListener('keydown', handleUserKeyPress)
      }
    }, [sections, handleUserKeyPress])

    return (
      <>
        <ComingSoon onClick={() => setModal(false)} isOpen={modal} />
        {sections.map((section, index) => (
          <DashboardSection
            key={section.url}
            {...section}
            section_progress={section_progress}
            index={index}
            openComingSoonModal={openComingSoonModal}
            sectionActive={sectionActive}
            setActiveUrl={setActiveUrl}
          />
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
