import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'
import CountryFinderModal from './CountryFinderModal'
import BasketViewer from './BasketView'

export const CountryFinderButton = () => {
  const [modalIsOpen, setIsOpen] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(true)
  const [selectedMarketID, setSelectedMarketID] = useState(null)
  const [selectedMarketName, setSelectedMarketName] = useState(null)

  const { markets, setMarkets, loadMarkets, addMarketItem } = useUserMarkets(false)

  const sortMap = sortMapBy(markets || [], 'country_name')

  const deleteMarket = (index) => {
    const reduced = [...markets]
    reduced.splice(index, 1)
    setMarkets(reduced)
    setSelectedMarketID(null)
    setSelectedMarketName(null)
    setIsDropdownOpen(false)
  }

  const selectCountry = (country) => {
    if (markets) {
      addMarketItem(country)
    }
  }

  console.log('markets', markets)

  return (
    <span>
      <BasketViewer dropdownOpen={isDropdownOpen} disabled={!markets.length} label="My markets" onOpen={loadMarkets}>

            {selectedMarketName && <div className="remove-confirmation">
              <div className="item-remove-title h-xs">
                Are you sure you want to remove {selectedMarketName} ?
              </div>
              <div className="remove-buttons">
                <button
                  type="button"
                  className="button button--primary"
                  onClick={() => {
                    deleteMarket(selectedMarketID)
                  }}
                >
                  Remove
                </button>
                <button
                  type="button"
                  className="button button--secondary"
                  onClick={() => {
                    setSelectedMarketName(null)
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>}

        {!selectedMarketName && <ul className="list m-v-0 body-l-b">
          {sortMap.map((marketIdx) => {
            const market = markets[marketIdx]
            return (
              <li className="p-v-xxs" key={`market-${marketIdx}`}>
                <button
                  type="button"
                  className="f-r button button--small button--only-icon button--tertiary"
                  onClick={() =>{
                    setSelectedMarketID(marketIdx)
                    setSelectedMarketName(market.country_name)
                  }}
                >
                  <i className="fas fa-times" />
                  <span className="visually-hidden">
                    Remove market {market.country_name}
                  </span>
                </button>
                {market.country_name}
              </li>
            )
          })}
        </ul>}
      </BasketViewer>
      {modalIsOpen && (
      <CountryFinderModal
        modalIsOpen
        setIsOpen={setIsOpen}
        selectCountry={selectCountry}
      />)}
    </span>
  )
}

export default function createCountryFinderButton({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(
    <Provider store={Services.store}>
      <CountryFinderButton />
    </Provider>,
    params.element
  )
}
