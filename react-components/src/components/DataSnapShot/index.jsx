import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { useSelector } from 'react-redux'
import { getEpProduct, getEpMarket } from '@src/reducers'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Table } from './Table'
import { ProductData } from './ProductData'


export const DataSnapShot = memo(
  ({ groups, selected, currentSection }) => {
    const product = useSelector((state) => getEpProduct(state))
    const country = useSelector((state) => getEpMarket(state))
    return (
      <>
        <h2 className="h-xs">Data Snapshot: { country.country_name }</h2>
        <ToggleSnapshot isOpen={false}>
          <div className="m-t-s" id="data-snapshot">
            <ProductData
              country={country}
              product={product}
            />
            <ToggleDataTable
              countryIso2Code={country.country_iso2_code}
              groups={groups}
              selectedGroups={selected}
              url={currentSection.url}
              afterTable={[<Table />]}
            />
          </div>
        </ToggleSnapshot>
      </>
    )
  }
)

DataSnapShot.propTypes = {
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

DataSnapShot.defaultProps = {
  groups: [],
  selected: [],
}
