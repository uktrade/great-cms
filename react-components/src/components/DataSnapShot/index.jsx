import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Table } from './Table'
import { ProductData } from './ProductData'

export const DataSnapShot = memo(
  ({ country, groups, insight, selected, currentSection }) => {
    const { import_from_world, import_data_from_uk, country_data } = insight[
      country
    ]

    return (
      <ToggleSnapshot isOpen={false}>
        <div className="m-t-s">
          <ProductData
            world={import_from_world}
            local={import_data_from_uk}
            country={country_data}
          />
          <ToggleDataTable
            country={country}
            groups={groups}
            selectedGroups={selected}
            url={currentSection.url}
          >
            <Table />
          </ToggleDataTable>
        </div>
      </ToggleSnapshot>
    )
  }
)

DataSnapShot.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  insight: PropTypes.shape({
    import_from_world: PropTypes.shape({
      year: PropTypes.string,
      trade_value: PropTypes.string,
      year_on_year_change: PropTypes.string,
    }).isRequired,
    import_data_from_uk: PropTypes.shape({
      year: PropTypes.string,
      trade_value: PropTypes.string,
    }).isRequired,
    country_data: PropTypes.shape({
      gdp_per_capita: PropTypes.shape({
        year_2019: PropTypes.string,
      }),
    }),
  }).isRequired,
}

DataSnapShot.defaultProps = {
  groups: [],
}
