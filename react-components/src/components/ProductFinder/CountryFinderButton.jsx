import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'
import { Confirmation } from '@src/components/ConfirmModal/Confirmation'
import CountryFinderModal from './CountryFinderModal'
import BasketViewer from './BasketView'
import { Link } from "react-router-dom";


export const CountryFinderButton = () => {
  const [modalIsOpen, setIsOpen] = useState(false)
  const { markets, loadMarkets, addMarketItem, removeMarketItem, marketsLoaded } = useUserMarkets(false, 'Personalisation bar')

  const sortMap = sortMapBy(markets || [], 'country_name')

  const [deleteConfirm, setDeleteConfirm] = useState()

  const deleteMarket = (index) => {
    removeMarketItem(markets[index])
    setDeleteConfirm(null)
  }

  const selectCountry = (country) => {
    if (markets) {
      addMarketItem(country)
    }
  }

  const routePath = "/where-to-export"


  return (
    <span>
      <BasketViewer label="My markets" onOpen={loadMarkets}>
        <ul>
          {sortMap.length === 0 && marketsLoaded ? <li>My markets is empty</li>: null}
          {sortMap.map((marketIdx) => {
            const market = markets[marketIdx]
            return (
              <li key={`market-${marketIdx}`}>

               <a href={routePath} >{market.country_name}</a>
                  <button
                  type="button"
                  className="remove-product"
                  onClick={() => setDeleteConfirm({index: marketIdx})}
                >
                  <span role="img" className="fas fa-trash great-red-text" />
                  <span className="govuk-visually-hidden">
                    Remove market {market.country_name}
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
        <button
          type="button"
          className="button primary-button button--icon m-t-xs button--full-width govuk-!-display-none"
          onClick={() => setIsOpen(true)}
        >
          <span className="fas fa-plus govuk-!-margin-righht-2" />
          Add market
        </button>
      </BasketViewer>
      {deleteConfirm && <Confirmation
        title={`Are you sure you want to remove ${markets[deleteConfirm?.index].country_name}?`}
        yesLabel="Remove"
        yesIcon="fa-trash-alt"
        onYes={() => deleteMarket(deleteConfirm.index)}
        onNo={() => setDeleteConfirm(null)}
      />}
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
