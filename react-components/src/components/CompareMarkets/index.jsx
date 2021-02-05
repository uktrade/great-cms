import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { getProducts } from '@src/reducers'
import { connect, Provider } from 'react-redux'
import { useCookies } from 'react-cookie'
import { analytics, get } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import ComparisonTables from './ComparisonTables'

const maxSelectedLength = 3

function CompareMarkets(props) {
  const { selectedProduct, tabs, ctaContainer } = props

  const cookieName = `comparisonMarkets_${get(Services, 'config.user.id')}`
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [cookies, setCookie] = useCookies([cookieName])

  const openModal = () => {
    setProductModalIsOpen(!selectedProduct)
    setMarketModalIsOpen(!!selectedProduct)
  }

  const comparisonMarkets = cookies[cookieName] || {}
  const selectedLength = Object.keys(comparisonMarkets).length || 0

  const pushAnalytics = (markets) => {
    const marketNames = Object.values(markets).map((v) => v.country_name)
    analytics({
      event: 'findMarketView',
      market1: marketNames[0] || '',
      market2: marketNames[1] || '',
      market3: marketNames[2] || '',
    })
  }

  const addCountry = (country) => {
    const newComparisonMarkets = cookies[cookieName] || {}
    newComparisonMarkets[country.country_iso2_code] = country
    setCookie(cookieName, newComparisonMarkets)
    pushAnalytics(newComparisonMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const tmpMarkets = cookies[cookieName] || {}
    delete tmpMarkets[id]
    setCookie(cookieName, tmpMarkets)
    pushAnalytics(tmpMarkets)
  }

  let buttonClass = 'button button--primary button--icon'
  let buttonLabel = 'Select product'
  if (selectedProduct) {
    buttonClass = `add-market m-t-xs ${buttonClass}`
    buttonLabel =
      selectedLength > 0
        ? `Add country ${selectedLength + 1} of ${maxSelectedLength}`
        : 'Add country to compare'
  }
  const triggerButton =
    selectedLength < maxSelectedLength ? (
      <button 
        type="button" 
        className={buttonClass} 
        onClick={openModal}
      >
        <i className="fa fa-plus-square" />
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
  }
}

const ConnectedCompareMarkets = connect(mapStateToProps)(CompareMarkets)

CompareMarkets.propTypes = {
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }),
  tabs: PropTypes.string.isRequired,
  ctaContainer: PropTypes.instanceOf(Element).isRequired,
}

CompareMarkets.defaultProps = {
  selectedProduct: null,
}

export default function createCompareMarkets({ ...params }) {
  const tabs = params.element.getAttribute('data-tabs')
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedCompareMarkets
        tabs={tabs}
        ctaContainer={params.cta_container}
      />
    </Provider>,
    params.element
  )
}
