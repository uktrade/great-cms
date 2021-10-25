import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import { useUserMarkets } from '@src/components/hooks/useUserData'
import { sortMapBy } from '@src/Helpers'
import CountryFinderModal from './CountryFinderModal'
import BasketViewer from './BasketView'
import { Confirmation } from '@src/components/ConfirmModal/Confirmation'

export const CountryFinderButton = () => {
  const [modalIsOpen, setIsOpen] = useState(false)
  const { markets, setMarkets, loadMarkets, addMarketItem } = useUserMarkets(false)

  const sortMap = sortMapBy(markets || [], 'country_name')

  const [deleteConfirm, setDeleteConfirm] = useState({
    delete: null,
    index: null,
    name: null
  })

  const confirmDelete = (name, index) => {
    setDeleteConfirm({
      delete: true,
      index: index,
      name: name
    })
  }

  const deleteMarket = (index) => {
    const reduced = [...markets]
    reduced.splice(index, 1)
    setMarkets(reduced)
    setDeleteConfirm({
      ...confirmDelete,
      delete: false
    })
  }

  const selectCountry = (country) => {
    if (markets) {
      addMarketItem(country)
    }
  }
  return (
    <span>
      <BasketViewer label="My markets" onOpen={loadMarkets}>
        {sortMap.length === 0 ? <p class="body-l-b text-center">My markets is empty</p>: null}
        <ul className="list m-v-0 body-l-b">
          {sortMap.map((marketIdx) => {
            const market = markets[marketIdx]
            return (
              <li className="p-v-xxs" key={`market-${marketIdx}`}>
                <button
                  type="button"
                  className="f-r button button--small button--only-icon button--tertiary"
                  // onClick={() => deleteMarket(marketIdx)}
                  onClick={() => confirmDelete(market.country_name, marketIdx)}
                >
                  <i className="fas fa-times fa-lg" />
                  <span className="visually-hidden">
                    Remove market {market.country_name}
                  </span>
                </button>
                {market.country_name}
              </li>
            )
          })}
        </ul>
      </BasketViewer>
      {deleteConfirm.delete && <Confirmation
        title={`Are you sure you want to remove ${deleteConfirm.name}?`}
        yesLabel="Remove"
        yesIcon="fa-trash-alt"
        onYes={() => deleteMarket(deleteConfirm.index)}
        onNo={() => setDeleteConfirm({...deleteConfirm, delete: false})}
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
