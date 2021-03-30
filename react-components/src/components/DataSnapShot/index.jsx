import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { useSelector } from 'react-redux'
import { getProducts, getMarkets } from '@src/reducers'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Table } from './Table'
import { ProductData } from './ProductData'


export const DataSnapShot = memo(
  ({ groups, selected, currentSection }) => {
    const product = useSelector((state) => getProducts(state))
    const country = useSelector((state) => getMarkets(state))

    return (<>
      <h2 className="h-xs p-t-l p-b-0">Data Snapshot: { country.country_name }</h2>
      <ToggleSnapshot isOpen={false}>
        <div className="m-t-s">
          <ProductData
            country={country}
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
      </>
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
  currentSection: PropTypes.shape({
    url: PropTypes.string,
  }).isRequired,
  selected: PropTypes.arrayOf(PropTypes.string.isRequired),
}

DataSnapShot.defaultProps = {
  groups: [],
  selected: [],
}
