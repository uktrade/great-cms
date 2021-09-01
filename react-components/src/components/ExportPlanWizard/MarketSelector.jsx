import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import CountryFinderModal from '@src/components/ProductFinder/CountryFinderModal'
import { sortBy } from '@src/Helpers'

function MarketSelector({ valueChange, selected, selectedProduct }) {
  const { markets, setMarkets, addMarketItem } = useUserMarkets()
  const [modalIsOpen, setModalIsOpen] = useState(false)
  const [addButtonShowing, setAddButtonShowing] = useState(false)

  let selectedKey

  let sortedMarkets = sortBy(markets || [], 'country_name')

  const options = sortedMarkets.map((market, index) => {
    if (selected && selected.country_iso2_code === market.country_iso2_code) {
      selectedKey = `${index}`
    }
    return {
      label: market.country_name,
      value: `${index}`,
    }
  })

  const somethingElse = {
    label: 'Something else',
    value: '+',
  }

  const onMarketChange = (index) => {
    setAddButtonShowing(index == '+')
    valueChange(sortedMarkets[index])
  }
  const onAddMarket = (market) => {
    setAddButtonShowing(false)
    addMarketItem(market)
    valueChange(market)
  }

  // If the add button is showing, 'something else' option must be selected
  selectedKey = selectedKey || (addButtonShowing ? '+' : '')

  const hasMarkets = markets && markets.length
  return (
    <>
      {hasMarkets ? (
        <div className="clearfix">
          <RadioButtons
            name="selected-market"
            choices={[...options, somethingElse]}
            valueChange={onMarketChange}
            initialSelection={selectedKey}
          />
        </div>
      ) : null}
      {(!hasMarkets || addButtonShowing) && (
        <div className="g-panel m-f-xxs">
          <button
            type="button"
            className="m-t-xxs m-t-xxs button button--primary"
            onClick={() => setModalIsOpen(true)}
          >
            <i className="fa fa-plus m-r-xxs" />
            Add a market
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
