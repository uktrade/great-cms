import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import CountryFinderModal from '@src/components/ProductFinder/CountryFinderModal'
import { sortBy } from '@src/Helpers'

function MarketSelector({ valueChange, selected, selectedProduct }) {
  const { markets, setMarkets, addMarketItem } = useUserMarkets()
  const [modalIsOpen, setModalIsOpen] = useState(false)

  let selectedIndex

  let sortedMarkets = sortBy(markets || [], 'country_name')

  const options = sortedMarkets.map((market, index) => {
    if (selected && selected.country_iso2_code === market.country_iso2_code) {
      selectedIndex = `${index}`
    }
    return {
      label: market.country_name,
      value: `${index}`,
    }
  })

  const addMarket = (market) => {
    addMarketItem(market)
    valueChange(market)
  }

  return (
    <>
      <div className="clearfix">
        <RadioButtons
          name="selected-market"
          choices={options}
          valueChange={(index) => valueChange(sortedMarkets[index])}
          initialSelection={selectedIndex}
        />
      </div>

      <button
        type="button"
        className="f-l m-t-xxs link"
        onClick={() => setModalIsOpen(true)}
      >
        <i className="fa fa-plus m-r-xxs" />
        Add a market
      </button>
      {modalIsOpen && (
        <CountryFinderModal
          modalIsOpen={modalIsOpen}
          setIsOpen={setModalIsOpen}
          selectCountry={addMarket}
          activeProducts={[selectedProduct]}
        />
      )}
    </>
  )
}

export default MarketSelector

MarketSelector.propTypes = {
  valueChange: PropTypes.func.isRequired,
  selected: PropTypes.shape({
    country_name: PropTypes.string,
    country_iso2_code: PropTypes.string,
  }),
  selectedProduct: PropTypes.shape({
    commodity_code: PropTypes.string,
    commodity_name: PropTypes.string,
  }),
}

MarketSelector.defaultProps = {
  selected: null,
  selectedProduct: null,
}
