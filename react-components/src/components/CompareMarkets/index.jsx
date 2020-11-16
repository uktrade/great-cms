import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie';
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'
import Services from '@src/Services'


const maxSelectedLength = 3

function CompareMarkets(props) {
  const { product } = props;
  const [productModalIsOpen, setProductModalIsOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(product)
  const [marketModalIsOpen, setMarketModalIsOpen] = useState(false)
  const [cookies, setCookie] = useCookies(['comparisonMarkets']);
  const [populationData, setPopulationData] = useState([])

  const openModal = () => {
    setProductModalIsOpen(!selectedProduct)
    setMarketModalIsOpen(!!selectedProduct)
  }

useEffect(() => {
   if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
       const countries = Object.values(comparisonMarkets).map(function (country) {
        return country.country_name
      })
     Services.getPopulationByCountryData(countries).then((result) => {
       setPopulationData(Object.entries(result))
       }).finally(() => {
     })
   }
}, [cookies.comparisonMarkets]);


  const getCountryData = (country) => {
    if (populationData && populationData.length) {
      const country_data =  Object.values(populationData).find(x => x[1].country === country)
      return country_data ? country_data[1] : []
    }
  }


  const addCountry = (country) => {
    const comparisonMarkets = cookies.comparisonMarkets || {}
    comparisonMarkets[country.country_iso2_code] = country
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
      let populationCountryData = getCountryData(market.country_name)
      return (<tr key={`market-${market.country_iso2_code}`}>
        <td className="p-v-xs"><span className="body-l-b" id={`market-${market.country_iso2_code}`}>{market.country_name}</span><button type="button" onClick={removeMarket} data-id={market.country_iso2_code} aria-label={`Remove ${market.country_name}`}><i className="fa fa-times-circle"/></button></td>
        <td id={`market-total-population-${market.country_name}`}>{populationCountryData ? populationCountryData.total_population : ''}</td>
        <td id={`market-internet-usage-${market.country_name}`}>{populationCountryData && populationCountryData.internet_usage ? populationCountryData.internet_usage.value + ' %' : 'NA'}</td>
        <td id={`market-urban-population-${market.country_name}`}><h1>{populationCountryData ? populationCountryData.urban_population_percentage_formatted : ''}</h1></td>
        <td id={`market-rural-population-${market.country_name}`}><h1>{populationCountryData ? populationCountryData.rural_population_percentage_formatted : ''}</h1></td>
      <td>{populationCountryData && populationCountryData.cpi ? populationCountryData.cpi.value : 'NA'}</td></tr>)
    })
    dataTable = (
      <div className="table market-details m-h-m bg-white p-v-s p-b-s p-h-s radius">
        <table>
          <thead>
          <tr>
            <th></th>
            <th>Total population</th>
            <th>Access to internet</th>
            <th>Living in urban areas</th>
            <th>Living in rural areas</th>
            <th>Consumer Price Index</th>
          </tr>
          </thead>
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
