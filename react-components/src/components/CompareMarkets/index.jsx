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
import { analytics } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import ComparisonTables from './ComparisonTables'

function CompareMarkets(props) {
  const { tabs, maxPlaces, ctaContainer, container } = props
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [selectedProducts] = useUserProducts()
  const [comparisonMarkets, _setComparisonMarkets] = useComparisonMarkets()
  const [activeProduct] = useActiveProduct(false)

  const cacheVersion = useSelector((state) => getCacheVersion(state))

  const hasSelectedProducts = selectedProducts && selectedProducts.length

  const selectedLength = Object.keys(comparisonMarkets || []).length

  const pushAnalytics = (markets) => {
    const marketNames = Object.values(markets).map((v) => v.country_name)
    analytics({
      event: 'findMarketView',
      market1: marketNames[0] || '',
      market2: marketNames[1] || '',
      market3: marketNames[2] || '',
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
  }

  const updateComparisonMarkets = (newMarkets) => {
    setComparisonMarkets(newMarkets)
    pushAnalytics(newMarkets)
    container.focus()
  }

  const addCountry = (country) => {
    const newMarkets = { ...comparisonMarkets }
    newMarkets[country.country_iso2_code] = country
    updateComparisonMarkets(newMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const newMarkets = { ...comparisonMarkets }
    delete newMarkets[id]
    updateComparisonMarkets(newMarkets)
  }

  const addProductButton = (
    <button
      type="button"
      className="button button--primary button--icon"
      onClick={() => setProductModalIsOpen(true)}
    >
      <i className="fa fa-plus-square" />
      Select product
    </button>
  )

  const addMarketButton = (
    <button
      type="button"
      className="button button--primary button--icon add-market m-t-xs"
      onClick={() => setMarketModalIsOpen(true)}
    >
      <i className="fa fa-plus-square" />
      {selectedLength > 0
        ? `Add place ${selectedLength + 1} of ${maxPlaces}`
        : 'Add a place'}
    </button>
  )

  return (
    <span>
      {hasSelectedProducts || selectedLength ? (
        <ComparisonTables
          tabsJson={tabs}
          comparisonMarkets={comparisonMarkets}
          activeProduct={activeProduct}
          removeMarket={removeMarket}
          triggerButton={addMarketButton}
          cacheVersion={cacheVersion}
        />
      ) : (
        ReactDOM.createPortal(addProductButton, ctaContainer)
      )}
      <ProductFinderModal
        modalIsOpen={productModalIsOpen}
        setIsOpen={setProductModalIsOpen}
      />
      <CountryFinderModal
        modalIsOpen={marketModalIsOpen}
        setIsOpen={setMarketModalIsOpen}
        activeProducts={activeProduct ? [activeProduct] : selectedProducts}
        addButton={false}
        selectCountry={addCountry}
        isCompareCountries
      />
    </span>
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
