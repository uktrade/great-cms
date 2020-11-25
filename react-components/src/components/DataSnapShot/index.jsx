import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { Table } from './Table'
import { CountryData } from './CountryData'

export const DataSnapShot = memo(({
  country,
  groups,
  selectedGroups,
  countryData
}) => {
  const [toggle, setToggle] = useState(false)

  return (
    <>
      <div className={`m-t-s ${ toggle ? '' : 'hidden'}`}>
          <CountryData
            country={country}
          />
          <ToggleDataTable
            country={country}
            groups={groups}
            selectedGroups={selectedGroups}
            countryData={countryData}
          >
            <Table />
          </ToggleDataTable>
      </div>
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
  selectedGroups: PropTypes.arrayOf(PropTypes.string.isRequired),
  countryData: PropTypes.arrayOf(PropTypes.string.isRequired)
}

DataSnapShot.defaultProps = {
  groups: [],
  selectedGroups: [],
  countryData: []
}
