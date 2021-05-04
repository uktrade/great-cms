import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import actions from '@src/actions'
import { getProducts, getCacheVersion } from '@src/reducers'
import { connect, Provider } from 'react-redux'
import { analytics } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import ComparisonTables from './ComparisonTables'

function CompareMarkets(props) {
  const { selectedProduct, tabs, maxPlaces, ctaContainer, cacheVersion } = props
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [comparisonMarkets, _setComparisonMarkets] = useState({})

  const userDataName = 'ComparisonMarkets'
  const openModal = () => {
    setProductModalIsOpen(!selectedProduct)
    setMarketModalIsOpen(!!selectedProduct)
  }

  const selectedLength = Object.keys(comparisonMarkets).length || 0

  useEffect(() => {
    Services.getUserData(userDataName).then((result) => {
      _setComparisonMarkets(result.data || {})
      Services.store.dispatch(actions.setCompareMarketList(result.data || {}))
    })
  }, [])

  const pushAnalytics = (markets) => {
    const marketNames = Object.values(markets).map((v) => v.country_name)
    analytics({
      event: 'findMarketView',
      market1: marketNames[0] || '',
      market2: marketNames[1] || '',
      market3: marketNames[2] || '',
    })
  }

  const setComparisonMarkets = (newMarkets) => {
    Services.setUserData(userDataName, newMarkets).then(() => {
      _setComparisonMarkets(newMarkets)
      Services.store.dispatch(actions.setCompareMarketList(newMarkets))
      pushAnalytics(newMarkets)
    })
  }

  const addCountry = (country) => {
    const newMarkets = { ...comparisonMarkets }
    newMarkets[country.country_iso2_code] = country
    setComparisonMarkets(newMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const newMarkets = { ...comparisonMarkets }
    delete newMarkets[id]
    setComparisonMarkets(newMarkets)
  }

  let buttonClass = 'button button--primary button--icon'
  let buttonLabel = 'Select product'
  if (selectedProduct) {
    buttonClass = `add-market m-t-xs ${buttonClass}`
    buttonLabel =
      selectedLength > 0
        ? `Add place ${selectedLength + 1} of ${maxPlaces}`
        : 'Add a place'
  }
  const triggerButton =
    selectedLength < maxPlaces ? (
      <button
        type="button"
        className={buttonClass}
        onClick={openModal}>
        <i className="fa fa-plus-square"
      />
        {buttonLabel}
      </button>
    ) : (
      <></>
    )
  let tabsContainer
  if (selectedProduct && selectedLength) {
    tabsContainer = (
      <ComparisonTables
        tabsJson={tabs}
        comparisonMarkets={comparisonMarkets}
        selectedProduct={selectedProduct}
        removeMarket={removeMarket}
        triggerButton={triggerButton}
        cacheVersion={cacheVersion}
      />
    )
  }

  return (
    <span>
      {tabsContainer}
      {(!selectedProduct || !selectedLength) &&
        ReactDOM.createPortal(triggerButton, ctaContainer)}

      <ProductFinderModal
        modalIsOpen={productModalIsOpen}
        setIsOpen={setProductModalIsOpen}
      />
      <CountryFinderModal
        modalIsOpen={marketModalIsOpen}
        setIsOpen={setMarketModalIsOpen}
        commodityCode={selectedProduct && selectedProduct.commodity_code}
        addButton={false}
        selectCountry={addCountry}
        isCompareCountries
      />
    </span>
  )
}

const mapStateToProps = (state) => {
  return {
    selectedProduct: getProducts(state),
    cacheVersion: getCacheVersion(state),
  }
}

const ConnectedCompareMarkets = connect(mapStateToProps)(CompareMarkets)

CompareMarkets.propTypes = {
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }),
  cacheVersion: PropTypes.number,
  tabs: PropTypes.string.isRequired,
  maxPlaces: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    .isRequired,
  ctaContainer: PropTypes.instanceOf(Element).isRequired,
}

CompareMarkets.defaultProps = {
  selectedProduct: null,
  cacheVersion: null,
}

export default function createCompareMarkets({ ...params }) {
  const tabs = params.element.getAttribute('data-tabs') || '{}'
  const maxPlaces = params.element.getAttribute('data-max-places-allowed') || 10
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedCompareMarkets
        tabs={tabs}
        maxPlaces={maxPlaces}
        ctaContainer={params.cta_container}
      />
    </Provider>,
    params.element
  )
}
