import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { getMarkets } from '@src/reducers'
import { useSelector } from 'react-redux'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { Table } from './Table'

export const TargetAgeGroupInsights = memo(
  ({ groups, selected, currentSection }) => {
    const country = useSelector((state) => getMarkets(state))
    return (
      <ToggleDataTable
        countryIso2Code={country.country_iso2_code}
        groups={groups}
        selectedGroups={selected}
        url={currentSection.url}
      >
        <Table />
      </ToggleDataTable>
    )
  }
)

TargetAgeGroupInsights.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  currentSection: PropTypes.shape({
    url: PropTypes.string,
  }).isRequired,
  selected: PropTypes.arrayOf(PropTypes.string.isRequired),
}

TargetAgeGroupInsights.defaultProps = {
  groups: [],
  selected: [],
}
