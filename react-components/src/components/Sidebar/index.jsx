import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import { CountryNotSelected } from '@src/components/Sidebar/CountryNotSelected'
import { ProductNotSelected } from '@src/components/Sidebar/ProductNotSelected'

export const Sidebar = memo(
  ({ sections, logo, company, currentSection, backUrl, epTitle }) => {
    const [toggle, setToggle] = useState(false)
    const [modal, setModal] = useState(false)

    return (
      <>
        <ComingSoon onClick={() => setModal(false)} isOpen={modal} />
        <ProductNotSelected
          isOpen={currentSection.product_required}
          backUrl={backUrl}
        />
        <CountryNotSelected
          backUrl={backUrl}
          isOpen={
            currentSection.country_required && !currentSection.product_required
          }
        />
        <nav
          className={`sidebar p-f-s p-r-m p-b-m ${!toggle && 'sidebar__close'}`}
          id="collapseNav"
          role="navigation"
        >
          <div className="sidebar-sticky">
            <button
              aria-expanded={toggle}
              aria-controls="collapseNav"
              type="button"
              className="sidebar__button text-blue-deep-40"
              onClick={() => setToggle(!toggle)}
            >
              <i
                className={`fas fa-angle-double-${toggle ? 'left' : 'right'}`}
              />
              <span className="visually-hidden">{toggle ? 'Close' : 'Expand'}</span>
            </button>
            <div className="text-center width-full p-t-m hidden">
              {logo ? (
                <img
                  src={logo}
                  alt={company}
                  className="m-f-auto m-r-auto w-1-2"
                />
              ) : (
                <img
                  src="https://via.placeholder.com/200/dfd5c5?text=Company logo"
                  alt="Add a business logo"
                  className="m-f-auto m-r-auto w-1-2"
                />
              )}
            </div>
            <p className="body-l-b">{epTitle}</p>
            <ul>
              {sections.map(({ title, url, disabled, is_complete }) => (
                <li className="" key={url}>
                  {disabled ? (
                    <button
                      className="link text-blue-deep-60 body-m"
                      type="button"
                      onClick={() => setModal(true)}
                    >
                      {title}
                    </button>
                  ) : (
                    <a
                      href={url}
                      className="link text-blue-deep-60 body-m-b"
                      title={title}
                    >
                    <i className={`fas ${ is_complete ? 'fa-check-circle text-green-100' : 'fa-circle text-black-10'} m-r-xxs`}></i>
                      <div className='inline-block'>{title}</div>
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </nav>
      </>
    )
  }
)

Sidebar.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string,
      url: PropTypes.string,
      disabled: PropTypes.bool,
    })
  ).isRequired,
  logo: PropTypes.string,
  company: PropTypes.string,
  currentSection: PropTypes.shape({
    title: PropTypes.string,
    url: PropTypes.string,
    disabled: PropTypes.bool,
    country_required: PropTypes.bool,
    product_required: PropTypes.bool,
  }).isRequired,
  backUrl: PropTypes.string.isRequired,
  epTitle: PropTypes.string
}

Sidebar.defaultProps = {
  logo: '',
  company: '',
  epTitle: '',
}
