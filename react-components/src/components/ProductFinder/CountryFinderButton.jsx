import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserMarkets } from '@src/components/hooks/useUserData'

import CountryFinderModal from './CountryFinderModal'
import BasketViewer from './BasketView'

export const CountryFinderButton = () => {
  const [modalIsOpen, setIsOpen] = useState(false)
  const [markets, setMarkets, loadMarkets] = useUserMarkets(false)

  const onOpenView = () => {
    loadMarkets()
  }

  const openModal = () => {
    setIsOpen(true)
  }

  const deleteMarket = (index) => {
    const reduced = [...markets]
    reduced.splice(index, 1)
    setMarkets(reduced)
  }

  const selectCountry = (country) => {
    if (markets) {
      setMarkets([...markets, country])
    }
  }

  return (
    <span>
      <BasketViewer label="My markets" onOpen={onOpenView}>
        <ul className="list m-v-0 body-l-b">
          {(markets || []).map((market, index) => (
            <li className="p-v-xxs" key={`market-${market.country_iso2_code}`}>
              {market.country_name}
              <button
                type="button"
                className="f-r button button--small button--only-icon button--tertiary"
                onClick={() => deleteMarket(index)}
              >
                <i className="fas fa-trash-alt" />
                <span className="visually-hidden">
                  Remove market {market.country_name}
                </span>
              </button>
            </li>
          ))}
        </ul>
        <button type="button" className="button button--primary button--icon m-t-xs button--full-width"
          onClick={openModal}
        >
          <i className="fas fa-plus"/>
          Add market
        </button>
      </BasketViewer>
      <CountryFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        selectCountry={selectCountry}
      />
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
