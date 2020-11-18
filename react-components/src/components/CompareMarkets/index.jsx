import React, {useState} from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import {useCookies} from 'react-cookie';
import ProductFinderModal from '../ProductFinder/ProductFinderModal'
import {CountryFinderModal} from '../ProductFinder/CountryFinder'
import PopulationData from "./PopulationData";
import EconomicData from "./EconomicData";
import Tabs from "./Tabs";


const maxSelectedLength = 3

function CompareMarkets(props) {

  const {product} = props;
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
    delete (comparisonMarkets[id])
    setCookie('comparisonMarkets', comparisonMarkets)
  }

  const comparisonMarkets = cookies.comparisonMarkets || {}
  const selectedLength = Object.keys(comparisonMarkets).length || 0

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

  const showTab = (e) => {
    console.log(e.target.dataset.id)
  }

  return (
    <span>
      <div className="table market-details m-h-m bg-white p-v-s p-b-s p-h-s radius">
      <div>

      <Tabs>
        <div label="Population">
          population...
           <PopulationData
            comparisonMarkets={comparisonMarkets}
            removeMarket={removeMarket}/>
        </div>
        <div label="Economic">
          economics..
            <EconomicData
            comparisonMarkets={comparisonMarkets}
            removeMarket={removeMarket}/>
        </div>

      </Tabs>
    </div>



        {triggerButton}
        </div>
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
    code: PropTypes.string
  })
}

CompareMarkets.defaultProps = {
  product: {},
}

export default function createCompareMarkets({...params}) {
  let product = {
    name: params.element.getAttribute('data-productname'),
    code: params.element.getAttribute('data-productcode')
  }
  if (!product.name) {
    product = null;
  }
  ReactDOM.render(<CompareMarkets product={product}/>, params.element)
}
