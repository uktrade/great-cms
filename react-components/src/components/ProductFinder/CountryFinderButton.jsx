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
  const { markets, setMarkets, loadMarkets, addMarketItem } = useUserMarkets(false)

  const sortMap = sortMapBy(markets || [], 'country_name')

  const deleteMarket = (index) => {
    const reduced = [...markets]
    reduced.splice(index, 1)
    setMarkets(reduced)
  }

  const selectCountry = (country) => {
    if (markets) {
      addMarketItem(country)
    }
  }

  return (
    <span>
      <BasketViewer label="My markets" onOpen={loadMarkets}>
        <ul className="list m-v-0 body-l-b">
          {sortMap.map((marketIdx) => {
            const market = markets[marketIdx]
            return (
              <li className="p-v-xxs" key={`market-${marketIdx}`}>
                <button
                  type="button"
                  className="f-r button button--small button--only-icon button--tertiary"
                  onClick={() => deleteMarket(marketIdx)}
                >
                  <i className="fas fa-trash-alt" />
                  <span className="visually-hidden">
                    Remove market {market.country_name}
                  </span>
                </button>
                {market.country_name}
              </li>
            )
          })}
        </ul>
        <button
          type="button"
          className="button button--primary button--icon m-t-xs button--full-width"
          onClick={() => setIsOpen(true)}
        >
          <i className="fas fa-plus" />
          Add market
        </button>
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
