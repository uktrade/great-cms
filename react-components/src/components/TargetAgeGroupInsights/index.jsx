import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { getMarkets } from '@src/reducers'
import { useSelector } from 'react-redux'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { AgeGroupData } from './AgeGroupData'
import { DemoData } from './DemoData'

export const TargetAgeGroupInsights = memo(
  ({ groups, selected, currentSection }) => {
    const country = useSelector((state) => getMarkets(state))
    return (
      <>
        <h2 className="h-xs p-t-l p-b-s">
          Facts and figures about {country.country_name} to get you started
        </h2>
        <ToggleDataTable
          countryIso2Code={country.country_iso2_code}
          groups={groups}
          selectedGroups={selected}
          url={currentSection.url}
          afterTable={[<DemoData/>,<AgeGroupData/>]}
        />
      </>
    )
  }
)

TargetAgeGroupInsights.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
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
