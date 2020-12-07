import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { useCookies } from 'react-cookie';
import Services from '@src/Services'
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import CountryFinderModal from '../ProductFinder/CountryFinderModal'

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

  const comparisonMarkets = cookies.comparisonMarkets || {}
  const selectedLength = Object.keys(comparisonMarkets).length || 0

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map((country) => {
        return country.country_name
      })
      Services.getPopulationByCountryData(countries).then((result) => {
        setPopulationData(Object.entries(result))
      }).finally(() => {})
    }
  }, [cookies.comparisonMarkets]);


  const getCountryData = (country) => {
    let countryData
    if (populationData && populationData.length) {
      countryData = Object.values(populationData).find(x => x[1].country === country)
    }
    return countryData ? countryData[1] : []
  }

  const addCountry = (country) => {
    const newComparisonMarkets = cookies.comparisonMarkets || {}
    newComparisonMarkets[country.country_iso2_code] = country
    setCookie('comparisonMarkets', newComparisonMarkets)
  }

  const removeMarket = (evt) => {
    const id = evt.target.closest('button').getAttribute('data-id')
    const tmpMarkets = cookies.comparisonMarkets || {}
    delete(tmpMarkets[id])
    setCookie('comparisonMarkets', tmpMarkets)
  }

  let triggerButton
  if (!selectedProduct) {
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

  const normalisePopulationValues = (str) => {
    if (str) {
      var values = str.replace(/\d+(\.\d+)?/g, ($0) => {
        return Math.round(parseFloat($0) * 10) / 10;
      })
      values = values.replace(/\d+(\.\d+)?(?=\%)/g, ($0) => {
        return Math.round($0);
      })
      return values.split(/\(([^)]+)\)/);
    } else {
      return 'Data not available';
    }
  }

  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {

    const tableBody = Object.values(comparisonMarkets).map(market => {
      const populationCountryData = getCountryData(market.country_name)
      return (<tr key={`market-${market.country_iso2_code}`} id={`market-${market.country_name}`}>
        <td className="p-v-xs name">
          <div style={{whiteSpace:'nowrap'}}>
            <button type="button" 
              onClick={removeMarket} 
              className="iconic" 
              data-id={market.country_iso2_code} 
              aria-label={`Remove ${market.country_name}`}>
              <i className="fa fa-trash-alt icon--border"/>
            </button>
            <span className="body-l-b" id={`market-${market.country_name}`}>{market.country_name}</span>
          </div>
        </td>
        <td className="total-population">{populationCountryData ? normalisePopulationValues(populationCountryData.total_population) : ''}</td>
        <td className="internet-usage">{populationCountryData && populationCountryData.internet_usage ? normalisePopulationValues(`${populationCountryData.internet_usage.value}%`) : 'Data not available'}</td>
        <td className="urban-population">
          <h1>{populationCountryData ? normalisePopulationValues(populationCountryData.urban_population_percentage_formatted)[0] : ''}</h1>
          <span className="body-m">{populationCountryData ? normalisePopulationValues(populationCountryData.urban_population_percentage_formatted)[1] : ''}</span>
        </td>
        <td className="rural-population">
          <h1>{populationCountryData ? normalisePopulationValues(populationCountryData.rural_population_percentage_formatted)[0] : ''}</h1>

          <span className="body-m">{populationCountryData ? normalisePopulationValues(populationCountryData.rural_population_percentage_formatted)[1] : ''}</span>
        </td>
      <td>{populationCountryData && populationCountryData.cpi ? populationCountryData.cpi.value : 'Data not available'}</td></tr>)
    })
    dataTable = (
      <div className="table market-details m-h-m bg-white p-v-s p-b-s p-h-s radius">
        <table>
          <thead>
            <tr>
              <th>&nbsp;</th>
              <th>Total Population</th>
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
  if (!product.name) {
    product = null;
  }
  ReactDOM.render(<CompareMarkets product={product} />, params.element)
}
