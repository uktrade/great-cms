import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import RegionToggle from './RegionToggle'
import Confirmation from './MessageConfirmation'


const suggested = [{'country':'France', 'region':'Europe'}, {'country': 'Spain', 'region':'Europe'}, {'country':'Italy', 'region':'Europe'}, {'country':'Jamaica',  'region':'Latin America and Caribbean'}]

export function CountryFinder(props) {
  let modalContent
  const { text } = props
  const [modalIsOpen, setIsOpen] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState(text)
  const [countryList, setCountryList] = useState()
  const [searchStr, setSearchStr] = useState()
  const [productConfirmationRequired, setProductConfirmationRequired] = useState(false)
  const [expandRegion, setExpandRegion] = useState(false)

  const openModal = () => {
    setProductConfirmationRequired(!!selectedCountry)
    setIsOpen(!selectedCountry)
    setSearchStr('')
  }

  const closeModal = () => {
    setProductConfirmationRequired(false)
    setIsOpen(false)
  }

  const closeConfirmation = () => {
    setProductConfirmationRequired(false)
    setIsOpen(true)
  }

  const searchChange = (evt) => {
    setSearchStr(evt.target.value.toUpperCase())
    setExpandRegion(true)
  }

  const toggleRegion = () => {
    setExpandRegion(!expandRegion)
  }

  const getCountries = () => {
    Services.getCountries().then((result) => {
      // map regions
      const regions = {}
      result.map((country) => {
        const { region } = country;
        (regions[region] = regions[region] || []).push(country)
        return null
      })
      setCountryList(regions)
    })  
  }

  const modalAfterOpen = () => {
    modalContent.style.maxHeight = '700px'
    if (!countryList) {
      getCountries()
    }
  }

  const saveCountry = (country) => {
    setSelectedCountry(country.name)
    let result = Services.updateExportPlan({
      export_countries: [
        {
          country_name: country.name,
          country_iso2_code: country.id,
          region: country.region
        }
      ]
    })
      .then((result) => {
        closeModal()
        window.location.reload()
      })
      .catch(() => {
        // TODO: Add error confirmation here
      })
  }

  const selectCountry = (evt) => {
    saveCountry({
      name: evt.target.getAttribute('data-country'),
      id: evt.target.getAttribute('data-id'),
      region: evt.target.getAttribute('data-region')
    })
  }

  let regions = Object.keys(countryList || {}).map((region, index) => {
    let countries = (countryList[region] || []).map((country, index) => {
      if (searchStr && country.name.toUpperCase().indexOf(searchStr) != 0) return ''
      return (
        <span className="c-1-5" key={index}>
          <li>
            <button type="button" className="link m-r-s m-b-xs" data-country={country.name} data-id={country.id} data-region={country.region} onClick={selectCountry}>
              {country.name}
            </button>
          </li>
        </span>
      )
    })
    return (
      !!countries.filter((countryRegion) => countryRegion).length && (
        <RegionToggle key={index} expandAllRegions={expandRegion} region={region} countries={countries} />
      )
    )
  })

  if (!regions.filter((region) => region).length) {
    regions = <div className="h-xs">No results found</div>
  }
  const suggestedList = suggested.map((value) => {
    return (
      <button key={`suggested_${value.country}`} type="button" className="tag tag--tertiary tag--icon m-r-s" data-country={value.country}  data-region={value.region} onClick={selectCountry}>
        {value.country}
      </button>
    )
  })

  const buttonClass = `tag ${!selectedCountry ? 'tag--tertiary' : ''} tag--icon `

  return (
    <span>
      <button type="button" className={buttonClass} onClick={openModal}>
        {selectedCountry || 'add country'}
        <i className={`fa ${(selectedCountry ? 'fa-edit' : 'fa-plus')}`}/>
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        className="modal max-modal"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => {modalContent = _modalContent; return null}}
      >
        <form className="country-chooser">
          <div style={{ height: '100px' }}>
            <button type="button" className="pull-right m-r-0 dialog-close" aria-label="Close" onClick={closeModal}/>
            <h2 className="h-m p-v-xs">Choose a target market</h2>
          </div>
          <div className="scroll-area" style={{ marginTop: '100px' }}>
            <div className="scroll-inner scroll-inner p-f-l p-r-l p-b-l p-t-xxs">
              <h3 className="h-s">Suggested markets</h3>
              <p className="m-v-xs">
                These are based on the size of the market for your product, export distance, tariffs and costs.
              </p>
              <ul className="m-v-xs">
                {suggestedList}
              </ul>
              <hr className="bg-black-70"/>

              <h3 className="h-s p-t-0">Compare markets</h3>
              <div className="grid">
                <div className="c-full">
                  <p className="m-v-xs">Compare stats for over 180 markets to find the best place to export.</p>
                  <a href="/" className="button button--secondary">
                    Compare markets
                  </a>
                </div>
              </div>

              <hr className="bg-black-70"/>
              <h3 className="h-s p-t-0">List of markets</h3>
              <p className="m-v-xs">
                If you have an idea of where you want to export, choose from the list below. You can change this at any
                time.
              </p>
              <div className="grid">
                <div className="c-1-3 search-input">
                  <input
                    className="form-control"
                    type="text"
                    onChange={searchChange}
                    onClick={searchChange}
                    defaultValue=""
                    placeholder="Search markets"
                  ></input>
                  <span className="visually-hidden">Search markets </span>
                  <i className="fas fa-search"></i>
                  
                </div>
              </div>
              <div className="grid">
                <div className="c-full">
                  <button type="button" key="region-expand" className="region-expand link" onClick={toggleRegion}>{expandRegion ? 'Collapse all' : 'Expand all' }</button>
                    <hr/>
                  <ul className="country-list" onClick={selectCountry}>
                    {regions}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </form>
      </ReactModal>
      <Confirmation
        buttonClass={buttonClass}
        productConfirmation={productConfirmationRequired}
        handleButtonClick={closeConfirmation}
        messageTitle="Changing target market?"
        messageBody="if you've created an export plan, make sure you update it to reflect your new market. you can change target market at any time."
        messageButtonText="Got it"
      />
    </span>
  )
}

CountryFinder.propTypes = {
  text: PropTypes.string
}
CountryFinder.defaultProps = {
  text: null
}

export default function createCountryFinder({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  const text = params.element.getAttribute('data-text')
  ReactDOM.render(<CountryFinder text={text}/>, params.element)
}
