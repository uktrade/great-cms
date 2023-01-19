import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

export const ToggleSnapshot = memo(({
 isOpen,
 children
}) => {
  const [toggle, setToggle] = useState(isOpen)

  return (
    <>
      <div className={toggle ? '' : 'hidden'}>
      { children }
      </div>
      <div>
        <button
          className='button secondary-button button--icon'
          type='button'
          onClick={() => setToggle(!toggle)}
          aria-controls="data-snapshot"
          aria-expanded={toggle}
        >
          <i className='fas fa-chart-bar' />{`${toggle ? 'Hide' : 'Open'} Data Snapshot`}
        </button>
      </div>
    </>
  )
})

ToggleSnapshot.propTypes = {
  isOpen: PropTypes.bool,
  children: PropTypes.element.isRequired
}

ToggleSnapshot.defaultProps = {
  isOpen: false
}
