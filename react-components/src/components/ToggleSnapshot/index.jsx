import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

export const ToggleSnapshot = memo(({
 isOpen,
 children
}) => {
  const [toggle, setToggle] = useState(isOpen)

  return (
    <>
      { toggle && children }
      <div className='m-t-s'>
        <button
          className='button button--tertiary button--icon'
          type='button'
          onClick={() => setToggle(!toggle)}
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
