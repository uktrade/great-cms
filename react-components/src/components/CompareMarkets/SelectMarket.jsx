import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie';
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import { CountryFinderModal } from '../ProductFinder/CountryFinder'
import Services from '@src/Services'
import { analytics } from '../../Helpers'

import { connect, Provider } from 'react-redux'
import actions from '@src/actions'
import { getMarkets } from '@src/reducers'


function SelectMarket(props) {
  const { market, setMarket } = props;
  const [cookies, setCookie] = useCookies(['comparisonMarkets']);

  const saveToExportPlan = (country) => {
    setMarket(country)
    Services.updateExportPlan({
        export_countries: [{
          country_name: country.name,
          country_iso2_code: country.id,
          region: country.region
        }]
      })
      .then(() => {
        closeModal()
        window.location.reload()
      })
      .then(
        analytics({
          'event': 'addMarketSuccess',
          'suggestMarket': country.suggested ? country.name : '',
          'listMarket': country.suggested ? '' : country.name,
          'marketAdded': country.name
        })
      )
      .catch(() => {
        // TODO: Add error confirmation here
      })
  }

  const clickMarket = (market) => {
    saveToExportPlan(market)
  }

  console.log('market from redux', market)
  console.log('markets', cookies.comparisonMarkets || {})
  const marketList = Object.values(cookies.comparisonMarkets || {}).map((market) => {
    return (
      <li key={market.id} className="m-b-xs">
        <button type="button" className="tag tag--tertiary tag--icon" data-name={market.name} data-id={market.id} data-region={market.region} data-suggested={market.suggested} onClick={() => clickMarket(market)}>
          {market.name}<i className="fa fa-plus"/>
        </button>
      </li>)
  })

  return (
    <section className="grid bg-blue-deep-80 text-white">
      <div className="c-1-4">&nbsp;</div>
      <div className="c-1-2 p-v-m">
        <h2 className="h-m text-white">Ready to choose a country?</h2>
        <p>Choosing a country for your profile tailors your lessons and Export Plan for a better overall experience.</p>
        <p>Don't worry, you can change this at any time.</p>
        <ul>
          {marketList}
        </ul>
      </div>
    </section>
  )
}

const mapStateToProps = (state) => {
  console.log('mmap state to props', state)
  return {
    market: getMarkets(state)
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    setMarket: market => { dispatch(actions.setMarket(market))}
  }
}

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(SelectMarket)

export default function createSelectMarket({ ...params }) {
  ReactDOM.render(    
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>, params.element)
}
