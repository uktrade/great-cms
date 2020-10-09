import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'
import MessageConfirmation from './MessageConfirmation'
import RegionToggle from "./RegionToggle";


const suggested = ['France', 'Spain', 'Italy', 'Jamaica']

export function CountryFinder(props) {
  let modalContent
  const [modalIsOpen, setIsOpen] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState(props.text)
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

  const modalAfterOpen = () => {
    modalContent.style.maxHeight = '700px'
    if (!countryList) {
      getCountries()
    }
  }

  const searchChange = (evt) => {
    let searchString = evt.target.value
    setSearchStr(searchString.toUpperCase())
  }

  const toggleRegion = (evt) => {
    setExpandRegion(!expandRegion)
    evt.preventDefault()

  }

  const getCountries = () => {
    Services.getCountries().then((result) => {
      // map regions
      let regions = {}
      for (const [index, country] of result.entries()) {
        let region = country.region;
        (regions[region] = regions[region] || []).push(country)
      }
      setCountryList(regions)
    })
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
      })
      .catch((result) => {
        // TODO: Add error confirmation here
      })
  }

  const selectCountry = (evt) => {
    let targetCountry = evt.target.getAttribute('data-country')
    saveCountry({
      name: evt.target.getAttribute('data-country'),
      id: evt.target.getAttribute('data-id'),
      region: evt.target.getAttribute('data-region')
    })
  }

  let _regions = Object.keys(countryList || {}).map((region) => {
    let countryFound = false
    let _countries = (countryList[region] || []).map((country, index) => {
      if (searchStr && country.name.toUpperCase().indexOf(searchStr) != 0) return ''
      countryFound = true
      return (
        <li key={country.id}>
          <button type="button" className="link m-r-s m-b-xs" data-country={country.name} data-id={country.id} data-region={country.region}>
            {country.name}
          </button>
        </li>
      )
    })
    return (
      !!_countries.filter((region) => region).length && (
        <RegionToggle key={region.replace(/[\s,]+/g, '-').toLowerCase()} expandAllRegions={expandRegion} region={region} countries={_countries} />
      )
    )
  })

  if (!_regions.filter((region) => region).length) {
    _regions = <div className="h-xs">No results found</div>
  }
  const _suggested = []
  for (const [index, value] of suggested.entries()) {
    _suggested.push(
      <button key={index} type="button" className="tag tag--tertiary tag--icon m-r-s" data-country={value}>
        {value}
      </button>
    )
  }
  let buttonClass = 'tag ' + (!selectedCountry ? 'tag--tertiary' : '') + ' tag--icon '

  return (
    <span>
      <button className={buttonClass} onClick={openModal}>
        {selectedCountry || 'add country'}
        <i className={'fa ' + (selectedCountry ? 'fa-edit' : 'fa-plus')}></i>
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        className="modal max-modal"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => (modalContent = _modalContent)}
      >
        <form className="country-chooser">
          <div className="modal-header" style={{ height: '100px' }}>
            <button className="pull-right m-r-0 dialog-close" onClick={closeModal}></button>
            <h2 className="h-m p-v-xs">Choose a target market</h2>
          </div>
          <div className="scroll-area" style={{ marginTop: '100px' }}>
            <div className="scroll-inner scroll-inner p-f-l p-r-l p-b-l p-t-xxs">
              <h3 className="h-s">Suggested markets</h3>
              <p className="m-v-xs">
                These are based on the size of the market for your product, export distance, tariffs and costs.
              </p>
              <ul className="m-v-xs" onClick={selectCountry}>
                {_suggested}
              </ul>
              <hr className="bg-black-70"></hr>

              <h3 className="h-s p-t-0">Compare markets</h3>
              <div className="grid">
                <div className="c-full">
                  <p className="m-v-xs">Compare stats for over 180 markets to find the best place to export.</p>
                  <a href="#" className="button button--secondary">
                    Compare markets
                  </a>
                </div>
              </div>

              <hr className="bg-black-70"></hr>
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
                  <span className="visually-hidden">Search markets</span>
                  <i className="fas fa-search"></i>
                </div>
              </div>
              <div className="grid">
                <div className="c-full">
                  <button key="region-expand" className="region-expand" onClick={toggleRegion}>{expandRegion ? 'Collapse all' : 'Expand all' }</button>
                    <hr key="region-expand-hr" className="hr m-b-xxs"></hr>
                  <ul className="country-list" onClick={selectCountry}>
                    {_regions}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </form>
      </ReactModal>
      <MessageConfirmation
        buttonClass={buttonClass}
        productConfirmation={productConfirmationRequired}
        handleButtonClick={closeConfirmation}
        messsageTitle="Changing target market?"
        messageBody="if you've created an export plan, make sure you update it to reflect your new market. you can change target market at any time."
        messageButtonText="Got it"
      />
    </span>
  )
}

export default function({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  let text = params.element.getAttribute('data-text')
  ReactDOM.render(<CountryFinder text={text}></CountryFinder>, params.element)
}
