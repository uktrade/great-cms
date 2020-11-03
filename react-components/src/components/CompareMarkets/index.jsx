import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie';
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import { CountryFinderModal } from '../ProductFinder/CountryFinder'


const maxSelectedLength = 3

function CompareMarkets(props) {
  const { product } = props;
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(product)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [cookies, setCookie] = useCookies(['comparisonMarkets']);

  const openModal = () => {
    setProductModalIsOpen(!selectedProduct)
    setMarketModalIsOpen(!!selectedProduct)
  }

  const addCountry = (country) => {
    const comparisonMarkets = cookies.comparisonMarkets || {}
    comparisonMarkets[country.id] = country
    setCookie('comparisonMarkets', comparisonMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const comparisonMarkets = cookies.comparisonMarkets || {}
    delete(comparisonMarkets[id])
    setCookie('comparisonMarkets', comparisonMarkets)
  }

  const comparisonMarkets = cookies.comparisonMarkets || {}
  const selectedLength = Object.keys(comparisonMarkets).length || 0

  let triggerButton
  if(!selectedProduct) {
    triggerButton = (
      <button type="button" 
        className="button button--primary button--icon"
        onClick={openModal}>
          <i className="fa fa-plus-square"/>
        Select product
      </button>)
  } else if (selectedLength < maxSelectedLength) {
    triggerButton = (
      <button type="button" 
          className="add-market button button--primary button--icon"
          onClick={openModal}>
            <i className="fa fa-plus-square"/>
            Select market {selectedLength + 1} of 3
        </button>
    )
  }

  let dataTable

  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
    const tableBody = Object.values(comparisonMarkets).map(market => {
      return (<tr key={`market-${market.id}`}>
        <td><span className="body-l-b">{market.name}</span><button type="button" onClick={removeMarket} data-id={market.id} aria-label={`Remove ${market.name}`}><i className="fa fa-times-circle"/></button></td>
      </tr>)
    })
    dataTable = (
      <div className="table market-details m-h-m bg-white p-v-xs p-h-s radius">
        <table>
          <tbody>
            {tableBody}
          </tbody>
        </table>
        {triggerButton}
      </div>
    )
  } else {
    dataTable = (
      <section className="container">
        <div className="grid">
          <div className="c-1-4">&nbsp;</div>
          <div className="c-1-2">
            {triggerButton}
          </div>
          <div className="c-1-4">&nbsp;</div>
        </div>
      </section>
    )
  }

  return (
    <span>
      {dataTable}
      <ProductFinderModal 
        modalIsOpen={ productModalIsOpen }
        setIsOpen={ setProductModalIsOpen }
        setSelectedProduct={ setSelectedProduct }
      />
      <CountryFinderModal
        modalIsOpen={ marketModalIsOpen }
        setIsOpen={ setMarketModalIsOpen }
        commodityCode={ selectedProduct && selectedProduct.code }
        addButton={false}
        selectCountry={ addCountry }
      />
    </span>
  )
}

CompareMarkets.propTypes = {
  product: PropTypes.shape({
    name: PropTypes.string,
    code: PropTypes.string
  })
}

CompareMarkets.defaultProps = {
  product: {},
}

export default function createCompareMarkets({ ...params }) {
  let product = {
      name: params.element.getAttribute('data-productname'),
      code: params.element.getAttribute('data-productcode')
  }
  if(!product.name) {
    product = null;
  }
  ReactDOM.render(<CompareMarkets product={product} />, params.element)
}
