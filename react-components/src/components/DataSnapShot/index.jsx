import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { Table } from './Table'
import { ProductData } from './ProductData'

export const DataSnapShot = memo(({
  country,
  groups
}) => {
  const [toggle, setToggle] = useState(false)

  return (
    <>
      { toggle &&
        <div className='m-t-s'>
            <ProductData />
            <ToggleDataTable
              country={country}
              groups={groups}
            >
              <Table />
            </ToggleDataTable>
        </div>
      }
      <div className='m-t-s'>
        <button
          className='button button--tertiary button--icon'
          type='button'
          onClick={() => setToggle(!toggle)}
        >
          <i className='fas fa-chart-bar' />Open Data Snapshot
        </button>
      </div>
    </>
  )
})

DataSnapShot.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired
  })),
}

DataSnapShot.defaultProps = {
  groups: []
}
