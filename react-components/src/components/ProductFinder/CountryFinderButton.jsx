import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import { Provider, useSelector } from 'react-redux'

import actions from '@src/actions'
import { getMarkets } from '@src/reducers'
import Services from '@src/Services'

import CountryFinderModal from './CountryFinderModal'
import BasketViewer from './BasketView'

const userMarketsKey = 'UserMarkets'

export const CountryFinderButton = (props) => {
  const { commodityCode, market } = props
  const markets = useSelector((state) => getMarkets(state))

  const [modalIsOpen, setIsOpen] = useState(false)
  const [confirmationRequired, setConfirmationRequired] = useState(false)

  const loadUserMarkets = () => {
    // Load the market list into redux.  We'll be needing it later
    if (!markets)
      Services.getUserData(userMarketsKey).then((result) => {
        Services.store.dispatch(actions.setMarkets(result[userMarketsKey]))
      })
  }

  const onOpenView = () => {
    loadUserMarkets()
  }

  const openModal = () => {
    setIsOpen(true)
  }

  const deleteMarket = (index) => {
    const reduced = [...markets]
    reduced.splice(index,1)
    Services.store.dispatch(actions.setMarkets(reduced))
  }

  const selectCountry = (country) => {
    if (markets) {
      Services.store.dispatch(actions.setMarkets([...markets, country]))
    }
  }

  return (
    <span>
      <BasketViewer label="My markets" onOpen={onOpenView}>
        <ul className="list m-v-0">
          {(markets || []).map((market, index) => (
            <li key={`market-${market.country_iso2_code}`}>
              {market.country_name} <button className="f-r" onClick={() => deleteMarket(index)}><i className="fas fa-trash-alt"/><span className="visually-hidden">Remove market {market.country_name}</span></button>
            </li>
          ))}
        </ul>
        <button className="button button--primary m-t-xs" onClick={openModal}>
          Add market
        </button>
      </BasketViewer>
      <CountryFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        commodityCode={commodityCode}
        selectCountry={selectCountry}
        market={market}
      />
    </span>
  )
}

CountryFinderButton.propTypes = {
  commodityCode: PropTypes.string,
  market: PropTypes.shape({
    country_name: PropTypes.string,
    country_iso2_code: PropTypes.string,
    region: PropTypes.string,
  }),
}
CountryFinderButton.defaultProps = {
  commodityCode: '',
  market: null,
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
