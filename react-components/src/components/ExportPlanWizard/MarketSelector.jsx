import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import RadioButtons from '@src/components/Segmentation/RadioButtons'
import CountryFinderModal from '@src/components/ProductFinder/CountryFinderModal'

function MarketSelector({valueChange, selected}) {
  const [markets, setMarkets] = useUserMarkets()
  const [modalIsOpen, setModalIsOpen] = useState(false)

  let selectedIndex

  const options = (markets || []).map((market, index) => {
    if(selected &&(selected.country_iso2_code === market.country_iso2_code)) {
      selectedIndex = `${index}`
    }
    return {
      label: market.country_name,
      value: `${index}`,
    }
  })

  return (
    <>
      <div className="clearfix">
        <RadioButtons
          name="selected-market"
          choices={options}
          valueChange={(index) => valueChange(markets[index])}
          initialSelection={selectedIndex}
        />
      </div>

      <button
        type="button"
        className="f-l m-t-xxs button button--tertiary button--icon"
        onClick={() => setModalIsOpen(true)}
      >
        <i className="fa fa-plus-square" />
        Add a market
      </button>
      <CountryFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setModalIsOpen}
        selectCountry={(market) => setMarkets([...markets, market])}
      />
    </>
  )
}

export default MarketSelector

MarketSelector.propTypes={
  valueChange: PropTypes.func.isRequired,
  selected: PropTypes.shape({
    country_name: PropTypes.string,
    country_iso2_code: PropTypes.string
  })
}

MarketSelector.defaultProps = {
  selected: null
}
