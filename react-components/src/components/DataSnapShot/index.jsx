import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Table } from './Table'
import { ProductData } from './ProductData'

export const DataSnapShot = memo(({ country, groups }) => {
  return (
    <ToggleSnapshot isOpen={false}>
      <div className="m-t-s">
        <ProductData />
        <ToggleDataTable country={country} groups={groups}>
          <Table />
        </ToggleDataTable>
      </div>
    </ToggleSnapshot>
  )
})

DataSnapShot.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
}

DataSnapShot.defaultProps = {
  groups: [],
}
