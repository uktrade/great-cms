import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { formatLanguages } from '@src/components/TargetAgeGroupInsights/utils'
import { Table } from './Table'

export const TargetAgeGroupInsights = memo(
  ({ country, groups, insight, selected, currentSection }) => {
    const { cia_factbook_data, country_data } = insight
    return (
      <ToggleDataTable
        country={country}
        groups={groups}
        selectedGroups={selected}
        url={currentSection.url}
      >
        <Table
          population={country_data.total_population}
          cpi={country_data.consumer_price_index.value}
          internetData={`${country_data.internet_usage.value}% (${country_data.total_internet_usage})`}
          languages={
            cia_factbook_data.languages
              ? formatLanguages(cia_factbook_data.languages.language)
              : ''
          }
        />
      </ToggleDataTable>
    )
  }
)

TargetAgeGroupInsights.propTypes = {
  country: PropTypes.string.isRequired,
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
  insight: PropTypes.shape({
    country_data: PropTypes.shape({
      total_population: PropTypes.string,
      total_internet_usage: PropTypes.string,
      consumer_price_index: PropTypes.shape({
        value: PropTypes.string,
      }).isRequired,
      internet_usage: PropTypes.shape({
        value: PropTypes.string,
      }).isRequired,
    }),
    cia_factbook_data: PropTypes.shape({
      languages: PropTypes.shape({
        language: PropTypes.arrayOf(PropTypes.string.isRequired),
      }),
    }).isRequired,
  }).isRequired,
}

TargetAgeGroupInsights.defaultProps = {
  groups: [],
  selected: [],
}
