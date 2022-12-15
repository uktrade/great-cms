import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/RadioButtons'
import CountryFinderModal from '@src/components/ProductFinder/CountryFinderModal'
import { sortBy } from '@src/Helpers'

function MarketSelector({ valueChange, selected, selectedProduct }) {
  const { markets, addMarketItem, marketsLoaded } = useUserMarkets(true, 'Market selector')
  const [modalIsOpen, setModalIsOpen] = useState(false)
  const [addButtonShowing, setAddButtonShowing] = useState(false)

  let selectedKey

  // It's possible (during an update) that the selected market is not in the list of user markets
  // In this case, we need to bodge it into the list
  if (selected && selected.country_iso2_code) {
    if (
      !markets.filter((market) => selected.country_iso2_code === market.country_iso2_code)
        .length
    ) {
      markets.push(selected)
    }
  }

  const sortedMarkets = sortBy(markets || [], 'country_name')

  const options = sortedMarkets.map((market, index) => {
    if (selected && selected.country_iso2_code === market.country_iso2_code) {
      selectedKey = `${index}`
    }
    return {
      label: market.country_name,
      value: `${index}`,
    }
  })

  const somewhereElse = {
    label: 'Somewhere else',
    value: '+',
  }

  const onMarketChange = (index) => {
    setAddButtonShowing(index === '+')
    valueChange(sortedMarkets[index])
  }
  const onAddMarket = (market) => {
    setAddButtonShowing(false)
    addMarketItem(market)
    valueChange(market)
  }

  // If the add button is showing, 'somewhere else' option must be selected
  selectedKey = selectedKey || (addButtonShowing ? '+' : '')

  const hasMarkets = markets && markets.length
  return (
    <>
      {hasMarkets ? (
        <div className="clearfix">
          <RadioButtons
            name="selected-market"
            choices={[...options, somewhereElse]}
            valueChange={onMarketChange}
            initialSelection={selectedKey}
          />
        </div>
      ) : null}
      {((marketsLoaded && !hasMarkets) || addButtonShowing) && (
        <div className={`${addButtonShowing ? 'g-panel' : ''} m-f-xxs`}>
          <button
            type="button"
            className="m-t-xxs m-t-xxs primary-button"
            onClick={() => setModalIsOpen(true)}
          >
            <i className="fa fa-plus m-r-xxs" />
            Choose Market
          </button>
        </div>
      )}
      {modalIsOpen && (
        <CountryFinderModal
          modalIsOpen={modalIsOpen}
          setIsOpen={setModalIsOpen}
          selectCountry={onAddMarket}
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
