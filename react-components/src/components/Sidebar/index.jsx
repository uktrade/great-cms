import React, { useState } from 'react'
import PropTypes from 'prop-types'

export const Sidebar = ({
  sections,
  url,
  logo,
  company
}) => {
  const [toggle, setToggle] = useState(true)

  return (
    <nav className={`sidebar p-h-s p-b-m ${!toggle && 'sidebar__close'}`}>
      <button
        type='button'
        className='sidebar__button text-blue-deep-40'
        onClick={ () =>setToggle(!toggle) }
      >
        <i className={`fas fa-angle-double-${toggle ? 'left' : 'right'}`} />
      </button>
      <div className='text-center width-full p-t-m'>
        { logo ?
          <img src={logo} alt={company} className='m-f-auto m-r-auto w-1-2' /> :
          <img src='https://via.placeholder.com/200/dfd5c5?text=Company logo' alt='Add a business logo' className='m-f-auto m-r-auto w-1-2' />
        }
      </div>
      <ul>
        {sections.map(section => (
          <li className='p-b-xs p-r-xs'>
            <a href={`${url}${section}`} className='link text-blue-deep-60 body-m' id='sidebar-'>{section}</a>
          </li>
        ))}
      </ul>
      <div>
        <button type='button' className='button button--icon-center m-r-xxs' disabled><i className='fas fa-share text-blue-deep-60 icon--border'/></button>
        <button type='button' className='button button--icon-center' disabled><i className='fas fa-download text-blue-deep-60 icon--border'/></button>
      </div>
    </nav>
 )
}

Sidebar.propTypes = {
  sections: PropTypes.arrayOf(PropTypes.string).isRequired,
  url: PropTypes.string.isRequired,
  logo: PropTypes.string,
  company: PropTypes.string,
}

Sidebar.defaultProps = {
  logo: '',
  company: ''
}
