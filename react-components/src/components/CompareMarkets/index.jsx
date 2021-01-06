import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie'
import { analytics } from '../../Helpers'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import PopulationData from './PopulationData'
import EconomyData from './EconomyData'
import Tabs from './Tabs'
import { isObject } from '../../Helpers'

const maxSelectedLength = 3

function CompareMarkets(props) {
  const { product } = props
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(product)
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

  const buttonClass = `${
    selectedProduct ? 'add-market' : ''
  } button button--primary button--icon`
  let buttonLabel = 'Select product'
  if (selectedProduct) {
    buttonLabel =
      selectedLength > 0
        ? `Add country ${selectedLength + 1} of ${maxSelectedLength}`
        : 'Add country to compare'
  }
  const triggerButton =
    selectedLength < maxSelectedLength ? (
      <button type="button" className={buttonClass} onClick={openModal}>
        <i className="fa fa-plus-square" />
        {buttonLabel}
      </button>
    ) : (
      ''
    )

  let tabMap = {
    population: (
      <PopulationData
        comparisonMarkets={comparisonMarkets}
        removeMarket={removeMarket}
      />
    ),
    economy: (
      <EconomyData
        comparisonMarkets={comparisonMarkets}
        removeMarket={removeMarket}
        selectedProduct={selectedProduct}
      />
    ),
  }

  let tabsContainer

  if (selectedProduct && selectedLength) {
    let tabs = JSON.parse(props.tabs)
    if (!isObject(tabs)) {
      tabs = JSON.parse(tabs)
    }
    let listOfTabs
    if (tabs && Object.keys(tabs).length > 0) {
      listOfTabs = Object.keys(tabs).filter((key) => tabs[key])
    }
    if (listOfTabs) {
      tabsContainer = (
        <Tabs showTabs={listOfTabs.length > 1}>
          {listOfTabs.map((item) => {
            return (
              <div
                key={item}
                label={item.toUpperCase()}
                className="button button--small button--tertiary"
              >
                <div className="table market-details m-h-m bg-white p-v-s p-b-s p-h-s radius">
                  {tabMap[item]}
                  {triggerButton}
                </div>
              </div>
            )
          })}
        </Tabs>
      )
    }
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
        setSelectedProduct={setSelectedProduct}
      />
      <CountryFinderModal
        modalIsOpen={marketModalIsOpen}
        setIsOpen={setMarketModalIsOpen}
        commodityCode={selectedProduct && selectedProduct.code}
        addButton={false}
        selectCountry={addCountry}
      />
    </span>
  )
}

CompareMarkets.propTypes = {
  product: PropTypes.shape({
    name: PropTypes.string,
    code: PropTypes.string,
  }),
}

CompareMarkets.defaultProps = {
  product: {},
}

export default function createCompareMarkets({ ...params }) {
  let product = {
    name: params.element.getAttribute('data-productname'),
    code: params.element.getAttribute('data-productcode'),
  }
  if (!product.name) {
    product = null
  }
  let tabs = params.element.getAttribute('data-tabs')
  ReactDOM.render(
    <CompareMarkets product={product} tabs={tabs} />,
    params.element
  )
}
