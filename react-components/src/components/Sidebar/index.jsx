import React, { useState } from 'react'
import PropTypes from 'prop-types'

export const Sidebar = ({ sections, logo, company }) => {
  const [toggle, setToggle] = useState(false)

  return (
    <nav className={`sidebar p-h-s p-b-m ${!toggle && 'sidebar__close'}`} id="collapseNav">
      <div className="sidebar-sticky">
        <button
          aria-expanded={toggle}
          aria-controls="collapseNav"
          type="button"
          className="sidebar__button text-blue-deep-40"
          onClick={() => setToggle(!toggle)}
        >
          <i className={`fas fa-angle-double-${toggle ? 'left' : 'right'}`} />
        </button>
        <div className="text-center width-full p-t-m">
          {logo ? (
            <img src={logo} alt={company} className="m-f-auto m-r-auto w-1-2" />
          ) : (
            <img
              src="https://via.placeholder.com/200/dfd5c5?text=Company logo"
              alt="Add a business logo"
              className="m-f-auto m-r-auto w-1-2"
            />
          )}
        </div>
        <ul>
          {sections.map(({ title, url}) => (
            <li className="p-b-xs p-r-xs" key={url}>
              <a href={url} className="link text-blue-deep-60 body-m" title={title}>
                {title}
              </a>
            </li>
          ))}
        </ul>
        <div>
          <button type="button" className="button button--small button--only-icon button--tertiary m-r-xxs" disabled>
            <i className="fas fa-share text-blue-deep-60" />
          </button>
          <button type="button" className="button button--small button--only-icon button--tertiary" disabled>
            <i className="fas fa-download text-blue-deep-60" />
          </button>
        </div>
      </div>
    </nav>
  )
}

Sidebar.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string,
      url: PropTypes.string
    })
  ).isRequired,
  logo: PropTypes.string,
  company: PropTypes.string
}

Sidebar.defaultProps = {
  logo: '',
  company: ''
}
