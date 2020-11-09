import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Table } from './Table'
import { ToggleDataTable } from '@src/components/ToggleDataTable'

export const TargetAgeGroupInsights = memo(({
  country,
  groups
}) => {
  return (
    <ToggleDataTable
      country={country}
      groups={groups}
    >
      <Table/>
    </ToggleDataTable>
  )
})

TargetAgeGroupInsights.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired
  })),
}

TargetAgeGroupInsights.defaultProps = {
  groups: []
}
