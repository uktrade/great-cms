import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import { CountryNotSelected } from '@src/components/Sidebar/CountryNotSelected'

export const Sidebar = ({ sections, logo, company, currentSection }) => {
  const [toggle, setToggle] = useState(false)
  const [modal, setModal] = useState(false)

  return (
    <>
      <ComingSoon
        onClick={() => setModal(false)}
        isOpen={modal}
      />
      <CountryNotSelected
        isOpen={currentSection.country_required}
      />
      <nav className={`sidebar p-h-s p-b-m ${!toggle && 'sidebar__close'}`} id='collapseNav' role="navigation">
        <div className='sidebar-sticky'>
          <button
            aria-expanded={toggle}
            aria-controls='collapseNav'
            type='button'
            className='sidebar__button text-blue-deep-40'
            onClick={() => setToggle(!toggle)}
          >
            <i className={`fas fa-angle-double-${toggle ? 'left' : 'right'}`} />
          </button>
          <div className='text-center width-full p-t-m'>
            {logo ? (
              <img src={logo} alt={company} className='m-f-auto m-r-auto w-1-2' />
            ) : (
              <img
                src='https://via.placeholder.com/200/dfd5c5?text=Company logo'
                alt='Add a business logo'
                className='m-f-auto m-r-auto w-1-2'
              />
            )}
          </div>
          <ul>
            {sections.map(({ title, url, disabled }) => (
              <li className='p-b-xs p-r-xs' key={url}>
                {disabled ?
                  <button className='link text-blue-deep-60 body-m' type='button' onClick={() => setModal(true)}>{title}</button> :
                  <a href={url} className='link text-blue-deep-60 body-m' title={title}>
                    {title}
                  </a>
                }
              </li>
            ))}
          </ul>
          <div>
            <button type='button' className='button button--small button--only-icon button--tertiary m-r-xxs' disabled>
              <i className='fas fa-share text-blue-deep-60' />
            </button>
            <button type='button' className='button button--small button--only-icon button--tertiary' disabled>
              <i className='fas fa-download text-blue-deep-60' />
            </button>
          </div>
        </div>
      </nav>
    </>
  )
}

Sidebar.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string,
      url: PropTypes.string,
      disabled: PropTypes.bool
    })
  ).isRequired,
  logo: PropTypes.string,
  company: PropTypes.string,
  currentSection: PropTypes.shape({
    title: PropTypes.string,
    url: PropTypes.string,
    disabled: PropTypes.bool,
    country_required: PropTypes.bool
  }).isRequired
}

Sidebar.defaultProps = {
  logo: '',
  company: ''
}
