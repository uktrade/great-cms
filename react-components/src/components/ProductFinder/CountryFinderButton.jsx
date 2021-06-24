import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import { connect, Provider } from 'react-redux'

import actions from '@src/actions'
import { getMarkets, getProducts } from '@src/reducers'
import Services from '@src/Services'

import Confirmation from './MessageConfirmation'
import CountryFinderModal from './CountryFinderModal'

export const CountryFinderButton = (props) => {
  const { commodityCode, market, setMarket } = props
  const [modalIsOpen, setIsOpen] = useState(false)
  const [confirmationRequired, setConfirmationRequired] = useState(false)

  const openModal = () => {
    setConfirmationRequired(!!market)
    setIsOpen(!market)
  }

  const closeConfirmation = () => {
    setConfirmationRequired(false)
    setIsOpen(true)
  }

  const buttonClass = `tag ${!market ? 'tag--tertiary' : ''} tag--icon `
  const hasPlace = market && market.country_name

  const triggerButton = (
    <button type="button" className={buttonClass} onClick={openModal}>
      {hasPlace || 'add place'}
      <span className="visually-hidden">{hasPlace ? 'Edit' : 'Add'} place</span>
      <i className={`fa ${market ? 'fa-edit' : 'fa-plus'}`} aria-hidden="true" />
    </button>
  )

  return (
    <span>
      {triggerButton}
      <CountryFinderModal
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
        commodityCode={commodityCode}
        selectCountry={setMarket}
        market={market}
      />
      <Confirmation
        buttonClass={buttonClass}
        productConfirmation={confirmationRequired}
        handleButtonClick={closeConfirmation}
        messageTitle="Changing target market?"
        messageBody="If you've already started creating an export plan, make sure you update it to include your new market. You can change your target market at any time."
        messageButtonText="Got it"
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
  setMarket: PropTypes.func.isRequired,
}
CountryFinderButton.defaultProps = {
  commodityCode: '',
  market: null,
}

const mapStateToProps = (state) => {
  const product = getProducts(state)
  return {
    market: getMarkets(state),
    commodityCode: product && product.commodity_code,
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    setMarket: (market) => {
      dispatch(actions.setMarket(market))
    },
  }
}

const ConnectedContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CountryFinderButton)

export default function createCountryFinderButton({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer />
    </Provider>,
    params.element
  )
}
