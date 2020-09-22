import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'

const customStyles = {
  content: {
    top: '10%',
    left: '10%',
    width: '80%',
    border: 'none',
    height: '80%',
    padding: '40px 60px',
    overflow: 'none',
  },
  overlay: {
    background: 'rgb(45 45 45 / 45%)',
    zIndex: '3',
  },
}

//const countries = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Belize', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic' ];
const suggested = ['France', 'Spain', 'Italy', 'Jamaica']

export function CountryFinder(props) {
  let modalContent
  const [modalIsOpen, setIsOpen] = React.useState(false)
  const [selectedCountry, setSelectedCountry] = React.useState(props.text)
  const [countryList, setCountryList] = React.useState()
  const [searchStr, setSearchStr] = React.useState()

  const openModal = () => {
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
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

  const getCountries = () => {
    Services.getCountries().then((result) => {
      // map regions
      let regions = {}
      for (const [index, country] of result.entries()) {
        let region = country.region
        ;(regions[region] = regions[region] || []).push(country)
      }
      setCountryList(regions)
    })
  }

  const saveCountry = (country) => {
    setSelectedCountry(country.name)
    let result = Services.updateExportPlan({ export_countries: [{'country_name': country.name, 'country_iso2_code': country.id}] })
      .then((result) => {
        closeModal()
      })
      .catch((result) => {
        // TODO: Add error confirmation here
      })
  }

  const selectCountry = (evt) => {
    saveCountry({
      name: evt.target.getAttribute('data-country'),
      id: evt.target.getAttribute('data-id')
    });
  }

  let _regions = Object.keys(countryList || {}).map((region) => {
    let countryFound = false
    let _countries = (countryList[region] || []).map((country, index) => {
      if (searchStr && country.name.toUpperCase().indexOf(searchStr) != 0) return ''
      countryFound = true
      return (
        <li key={country.id}>
          <button type="button" className="link m-r-s m-b-xs" data-country={country.name} data-id={country.id}>
            {country.name}
          </button>
        </li>
      )
    })
    return (
      !!_countries.filter((region) => region).length && (
        <section key={region}>
          <div className="grid">
            <div className="c-full-width">
              <h2 className="h-xs">{region}</h2>
              <ul style={{ display: 'flex', flexWrap: 'wrap' }}>{_countries}</ul>
              <hr className="hr m-b-xxs"></hr>
            </div>
          </div>
        </section>
      )
    )
  })

  if (!_regions.filter((region) => region).length) {
    _regions = <div className="h-xs">No results found</div>
  }

  const _suggested = []
  for (const [index, value] of suggested.entries()) {
    _suggested.push(
      <button
        key={index}
        type="button"
        className="button button--ghost-blue button--round-corner button--chevron m-r-s"
        data-country={value}
      >
        {value}
      </button>
    )
  }

  return (
    <span>
      <button className="button button--primary button--round-corner" onClick={openModal}>
        {selectedCountry}
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
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
                    defaultValue=""
                    placeholder="Search markets"
                  ></input>
                  <span className="visually-hidden">Search markets</span>
                  <i className="fas fa-search"></i>
                </div>
              </div>
              <div className="grid">
                <div className="c-full">
                  <ul className="country-list" onClick={selectCountry}>
                    {_regions}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </form>
      </ReactModal>
    </span>
  )
}

export default function ({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(<CountryFinder text={params.element.innerText}></CountryFinder>, params.element)
}
