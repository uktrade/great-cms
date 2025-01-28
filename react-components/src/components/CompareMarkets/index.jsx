import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import {
  useUserProducts,
  useComparisonMarkets,
  useActiveProduct,
} from '@src/components/hooks/useUserData'
import { getCacheVersion } from '@src/reducers'
import { Provider, useSelector } from 'react-redux'
import { analytics, deepEqual } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import ComparisonTables from './ComparisonTables'
import SelectMarket from './SelectMarket'

function CompareMarkets({ tabs, maxPlaces, ctaContainer, container }) {
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const { products, productsLoaded } = useUserProducts()
  const [comparisonMarkets, _setComparisonMarkets] = useComparisonMarkets()
  const [activeProduct] = useActiveProduct()
  const cacheVersion = useSelector((state) => getCacheVersion(state))

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  console.log('COMPONENT INVOKED')
  const hasProducts = products && products.length
  const selectedLength = Object.keys(comparisonMarkets || []).length

  console.log("comparisonMarkets: " + comparisonMarkets)
  if (comparisonMarkets) {
    if (Object.keys(comparisonMarkets)) {
      console.log("Object.keys(comparisonMarkets: " + Object.keys(comparisonMarkets))
      console.log("typeof(comparisonMarkets): " + typeof(comparisonMarkets))
    }
    else {
      console.log("typeof(comparisonMarkets): " + typeof(comparisonMarkets))
    }
  }
  else {
    console.log("NOT DEFINED")
  }


  const pushAnalytics = (markets, market, remove) => {
    const marketNames = Object.values(markets).map((v) => v.country_name)
    analytics({
      event: remove ? 'removeMarketFromGrid':'addMarketToGrid',
      gridMarkets: marketNames.join('|'),
      [remove ? 'removedMarket':'gridMarketAdded']:market.country_name,
      marketCount: marketNames.length,
    })
  }

  const setComparisonMarkets = (markets) => {
    _setComparisonMarkets(markets)
    // Create an aria label with a list of selected countries
    const marketCount = Object.values(markets).length
    const label = Object.values(markets).reduce((str, market, index) => {
      const separator = index < marketCount - 1 ? ',' : ' and'
      return `${str}${index > 0 ? separator : ''} ${market.country_name}`
    }, 'Comparison information for')
    container.setAttribute('aria-label', label)
    container.focus()
  }

  const addCountry = (country) => {
    const newMarkets = { ...comparisonMarkets }
    newMarkets[country.country_iso2_code] = country
    pushAnalytics(newMarkets, country)
    setComparisonMarkets(newMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const newMarkets = { ...comparisonMarkets }
    delete newMarkets[id]
    pushAnalytics(newMarkets, comparisonMarkets[id], true)
    setComparisonMarkets(newMarkets)
  }

  const addProductButton = (
    <button
      type="button"
      className="button primary-button button--icon"
      onClick={() => setProductModalIsOpen(true)}
    >
      <span className="fa fa-plus govuk-!-margin-right-2" />
      Add product
    </button>
  )

  const addMarketButton = (
    <>
      {' '}
      {selectedLength < maxPlaces && (
        <button
          type="button"
          className="button primary-button button--icon add-market m-t-xs"
          onClick={() => setMarketModalIsOpen(true)}
        >
          <span className="fa fa-plus govuk-!-margin-right-2" />
          Add market
        </button>
      )}
    </>
  )

  const suggestedMarketsProducts = () => {
    // get the list of products for suggested markets in country chooser modal
    if (activeProduct) {
      const foundActive = (products || []).find((sProduct) =>
        deepEqual(sProduct, activeProduct)
      )
      return foundActive ? [foundActive] : products
    }
    return products
  }


  return (
    productsLoaded && (
      <>
        {selectedLength ? (
          <>
          <ComparisonTables
            tabsJson={tabs}
            comparisonMarkets={comparisonMarkets}
            activeProduct={activeProduct}
            removeMarket={removeMarket}
            triggerButton={addMarketButton}
            cacheVersion={cacheVersion}
          />
          {ReactDOM.createPortal( <p>
            Continue adding upto 10 markets to compare dynamic data from some of the world's most trusted sources.
          </p>, ctaContainer)}
          </>
        ) : (
          ReactDOM.createPortal(
            hasProducts ? (
              <>
                <p>
                 Find information to help choose the right export markets for your product. Add a market to see dynamic data from some of the world's most trusted sources.
                </p>
                {addMarketButton}
              </>
            ) : (
              <>
              <p>
                 Find information to help choose the right export markets for your product. Add a product to see dynamic data from some of the world's most trusted sources.
                </p>
                {addProductButton}
              </>
            ),
            ctaContainer
          )
        )}
        <ProductFinderModal
          modalIsOpen={productModalIsOpen}
          setIsOpen={setProductModalIsOpen}
        />
        {marketModalIsOpen && (
          <CountryFinderModal
            modalIsOpen
            setIsOpen={setMarketModalIsOpen}
            activeProducts={suggestedMarketsProducts()}
            addButton={false}
            selectCountry={addCountry}
            isCompareCountries
          />
        )}
        <SelectMarket />
      </>
    )
  )
}

CompareMarkets.propTypes = {
  tabs: PropTypes.string.isRequired,
  maxPlaces: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    .isRequired,
  ctaContainer: PropTypes.instanceOf(Element).isRequired,
  container: PropTypes.instanceOf(Element).isRequired,
}

export default function createCompareMarkets({ ...params }) {
  const tabs = params.element.getAttribute('data-tabs') || '{}'
  const maxPlaces = params.element.getAttribute('data-max-places-allowed') || 10
  ReactDOM.render(
    <Provider store={Services.store}>
      <CompareMarkets
        tabs={tabs}
        maxPlaces={maxPlaces}
        ctaContainer={params.cta_container}
        container={params.element}
      />
    </Provider>,
    params.element
  )
}
