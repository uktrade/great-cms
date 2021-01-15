import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { getProducts } from '@src/reducers'
import { connect, Provider } from 'react-redux'
import { useCookies } from 'react-cookie'
import { analytics } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import SocietyData from './SocietyData'
import { isObject } from '../../Helpers'
import ComparisonTables from './ComparisonTables'

const maxSelectedLength = 3

function CompareMarkets(props) {
  const { selectedProduct, tabs } = props
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [cookies, setCookie] = useCookies(['comparisonMarkets'])

  const openModal = () => {
    setProductModalIsOpen(!selectedProduct)
    setMarketModalIsOpen(!!selectedProduct)
  }

  const comparisonMarkets = cookies.comparisonMarkets || {}
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
    const newComparisonMarkets = cookies.comparisonMarkets || {}
    newComparisonMarkets[country.country_iso2_code] = country
    setCookie('comparisonMarkets', newComparisonMarkets)
    pushAnalytics(newComparisonMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const tmpMarkets = cookies.comparisonMarkets || {}
    delete tmpMarkets[id]
    setCookie('comparisonMarkets', tmpMarkets)
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
      <button type="button" 
        className={buttonClass} 
        onClick={openModal}
      >
        <i className="fa fa-plus-square" />
        {buttonLabel}
      </button>
    ) : (
      ''
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
  } else {
    // Either We're missing a product or any countries
    tabsContainer = (
      <section className="container">
        <div className="grid">
          <div className="c-1-4-l">&nbsp;</div>
          <div className="c-1-2-l">{triggerButton}</div>
        </div>
      </section>
    )
  }

  return (
    <span>
      {tabsContainer}
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
  tabs: PropTypes.string.isRequired
}

CompareMarkets.defaultProps = {
  selectedProduct: null,
}

export default function createCompareMarkets({ ...params }) {
  const tabs = params.element.getAttribute('data-tabs')
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedCompareMarkets tabs={tabs} />
    </Provider>,
    params.element
  )
}
