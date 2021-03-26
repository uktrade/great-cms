import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { useSelector } from 'react-redux'
import { getProducts, getMarkets } from '@src/reducers'
import { camelizeObject } from '@src/Helpers'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Table } from './Table'
import { ProductData } from './ProductData'


export const DataSnapShot = memo(
  ({ groups, insight, selected, currentSection }) => {
    const product = useSelector((state) => getProducts(state))
    const country = useSelector((state) => getMarkets(state))
    const { importFromWorld, importFromUk, countryData } = camelizeObject(
      insight[country.country_iso2_code] || {}
    )

    return (
      <ToggleSnapshot isOpen={false}>
        <div className="m-t-s">
          <ProductData
            world={importFromWorld || {}}
            local={importFromUk || {}}
            country={countryData || {}}
            product={product}
          />
          <ToggleDataTable
            countryIso2Code={country.country_iso2_code}
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
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  insight: PropTypes.shape({
    importFromWorld: PropTypes.shape({
      year: PropTypes.string,
      trade_value: PropTypes.string,
      year_on_year_change: PropTypes.string,
    }),
    importFromUk: PropTypes.shape({
      year: PropTypes.string,
      trade_value: PropTypes.string,
    }),
    countryData: PropTypes.shape({
      gdp_per_capita: PropTypes.shape({
        year_2019: PropTypes.string,
      }),
    }),
  }).isRequired,
  currentSection: PropTypes.shape({
    url: PropTypes.string,
  }).isRequired,
  selected: PropTypes.arrayOf(PropTypes.string.isRequired),
}

DataSnapShot.defaultProps = {
  groups: [],
  selected: [],
}
