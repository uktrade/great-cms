import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import Services from '@src/Services'
import { connect, Provider, useSelector } from 'react-redux'
import actions from '@src/actions'
import { getMarkets, getComparisonMarkets } from '@src/reducers'
import { analytics, get } from '../../Helpers'


function SelectMarket() {
  const comparisonMarkets = Object.values(useSelector((state) => getComparisonMarkets(state)).comparisonMarkets || {})
  const market = useSelector((state) => getMarkets(state))

  const clickMarket = (clickedMarket) => {
    const marketNames = comparisonMarkets.map((v) => v.country_name)
    Services.store.dispatch(actions.setMarket(clickedMarket))
    analytics({
      event: 'addFindMarketSuccess',
      market1: marketNames[0] || 'None',
      market2: marketNames[1] || 'None',
      market3: marketNames[2] || 'None',
      findMarket: clickedMarket.country_name,
    })
  }

  let isComparisonMarketSelected
  const marketList = comparisonMarkets.map((mapMarket) => {
    const isSelected =
      (market && market.country_iso2_code) === mapMarket.country_iso2_code
    isComparisonMarketSelected = isComparisonMarketSelected || isSelected
    return (
      <li key={mapMarket.country_iso2_code} className="m-b-xs">
        <button
          type="button"
          className={`tag tag--icon ${
            isSelected ? 'tag--primary' : 'tag--tertiary'
          } market-${mapMarket.country_iso2_code}`}
          onClick={() => clickMarket(mapMarket)}
        >
          {mapMarket.country_name}
          <i className={`fa ${isSelected ? 'fa-check' : 'fa-plus'}`} />
        </button>
      </li>
    )
  })

  const nextSteps = isComparisonMarketSelected ? (
    <section className="bg-red-90 p-h-xl p-v-s">
      <h2 className="h-s text-white p-t-0 p-b-xs">Next steps</h2>
      <div className="flex-grid">
        {ReactHtmlParser(document.getElementById('next-steps').innerHTML)}
      </div>
    </section>
  ) : (
    ''
  )

  return Object.keys(marketList).length ? (
    <div>
      <section className="grid bg-blue-deep-100 text-white">
        <div className="c-1-4">&nbsp;</div>
        <div className="c-1-2 p-v-m">
          <div className="p-h-xs">
            <h2 className="h-m text-white">Ready to choose a country?</h2>
            <p>
              Choosing a country for your profile tailors your lessons and
              Export Plan for a better overall experience.
            </p>
            <p>Don&apos;t worry, you can change this at any time.</p>
            <ul className="m-b-n-xs">{marketList}</ul>
          </div>
        </div>
      </section>
      {nextSteps}
    </div>
  ) : (
    ''
  )
}

export default function createSelectMarket({ ...params }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <SelectMarket />
    </Provider>,
    params.element
  )
}
