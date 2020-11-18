import React, { useState, useEffect } from 'react'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import RegionToggle from './RegionToggle'
import SearchInput from './SearchInput'
import { analytics } from '../../Helpers'


export default function CountryFinderModal(props) {
  let scrollOuter
  const { modalIsOpen, setIsOpen, commodityCode, selectCountry } = props
  const [countryList, setCountryList] = useState()
  const [suggestedCountries, setSuggestedCountries] = useState([])
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchStr, setSearchStr] = useState()
  const [expandRegion, setExpandRegion] = useState(false)

  useEffect(() => {
    if (modalIsOpen) {
      analytics({
        'event': 'addMarketPageview',
        'virtualPageUrl': '/choose-target-market-modal',
        'virtualPageTitle': 'Choose Target Market Modal'
      })
    }

  },[modalIsOpen])

  const closeModal = () => {
    setSearchStr('')
    setExpandRegion(false)
    setIsOpen(false)
  }

  const setScrollShadow = () => {
    if (scrollOuter) {
      const bottomOverflow = scrollOuter.scrollHeight - (scrollOuter.scrollTop + scrollOuter.clientHeight)
      setIsScrolled({ top: scrollOuter.scrollTop > 0, bottom: bottomOverflow > 0 })
    }
  }

  const onScroll = (evt) => {
    scrollOuter = evt.target
    setScrollShadow()
  }

  const searchChange = (value) => {
    setExpandRegion(value.length > 0)
    setSearchStr(value.toUpperCase())
  }

  const toggleRegion = () => {
    setExpandRegion(!expandRegion)
  }

  const getSuggestedCountries = () => {
    if (commodityCode) {
      const hs2 = commodityCode.substr(0, 2)
      Services.getSuggestedCountries(hs2).then((result) => {
        setSuggestedCountries(result);
      })
    }
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
    if (!countryList) {
      getCountries()
    }
    getSuggestedCountries()
  }

  const clickCountry = (evt) => {
    const country = {
      country_name: evt.target.getAttribute('data-country'),
      country_iso2_code: evt.target.getAttribute('data-id'),
      region: evt.target.getAttribute('data-region'),
      suggested: evt.target.getAttribute('data-suggested'),
    }
    selectCountry(country)
    closeModal()
  }

  let regions = Object.keys(countryList || {}).sort().map((region) => {
    const countries = (countryList[region] || []).map((country) => {
      if ((searchStr && country.name.toUpperCase().indexOf(searchStr) !== 0) || !region) return ''
      return (
        <span className="c-1-5" key={country.id}>
          <li>
            <button type="button" className="link m-r-s m-b-xs" data-country={country.name} data-id={country.id} data-region={country.region} onClick={clickCountry}>
              {country.name}
            </button>
          </li>
        </span>
      )
    })
    return (
      !!countries.filter((countryRegion) => countryRegion).length && (
        <RegionToggle key={region} expandAllRegions={expandRegion} region={region} countries={countries} />
      )
    )
  })

  if (!regions.filter((region) => region).length) {
    regions = <div className="h-xs">No results found</div>
  }

  /*   Suggested markets section  */
  let suggestedSection = (<div>
      <h3 className="h-s">Suggested markets</h3>
      <p className="m-v-xs">Add a product so that we can suggest export markets.</p>
  </div>)
  if (commodityCode) {
    const suggestedList = suggestedCountries.map((country) => {
      return (
        <button key={`suggested_${country.country_iso2}`} type="button" className="tag tag--tertiary tag--icon m-r-s m-v-xxs" data-country={country.country_name}  data-region={country.region} data-id={country.country_iso2} onClick={clickCountry} data-suggested>
          {country.country_name}
          <i className="fa fa-plus"/>
        </button>
      )
    })
    suggestedSection = (<div className="suggested-markets">
      <h3 className="h-s">Suggested markets</h3>
      <p className="m-v-xs">These are based on the size of the market for your product, export distance, tariffs and costs.</p>
      <ul className="m-v-xs">{suggestedList}</ul>
  </div>)
  }

  /*   Compare markets section  */
  const compareMarketsSection = !selectCountry && (
    <div>
      <hr className="hr bg-red-deep-100"/>
      <h3 className="h-s p-t-xs">Compare markets</h3>
      <div className="grid">
        <div className="c-full">
          <p className="m-v-xs">Compare stats for over 180 markets to find the best place to target your exports.</p>
          <a href="/find-your-target-market/" className="button button--secondary">
            Compare Markets
          </a>
        </div>
      </div>
    </div>
  )

  const scrollerClass = `scroll-area ${isScrolled && isScrolled.top ? 'scroll-shadow-top' : ''} ${isScrolled && isScrolled.bottom ? 'scroll-shadow-bottom' : ''}`

  return (
    <span>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        className="modal max-modal"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
        style={{
          content:{
            width:'auto',
            left: '100px',
            right: '100px',
            top: '50px',
            bottom: '50px',
            overflow: 'hidden',
          }
        }}
      >
        <div className="country-finder">
          <div className={`scroll-area m-t-0 ${scrollerClass}`} onScroll={onScroll}>
                <button type="button" className="f-r m-r-0 dialog-close" aria-label="Close" onClick={closeModal}/>
            <div
              className="scroll-inner scroll-inner p-f-l p-r-l p-b-l p-t-xxs"
              ref={(_scrollInner) => {scrollOuter = _scrollInner || scrollOuter}}
            >
              <div>
                <h2 className="h-l m-t-s p-b-xs">Choose a target market</h2>
              </div>
              {suggestedSection}
              {compareMarketsSection}
              <hr className="hr bg-red-deep-100"/>
              <h3 className="h-s p-t-xs">List of markets</h3>
              <p className="m-v-xs">
                If you have an idea of where you want to export, choose from the list below. <br/>You can change this at any
                time.
              </p>
              <div className="grid">
                <div className="c-1-3 search-input">
                  <SearchInput
                    onChange={searchChange}
                  />
                </div>
              </div>
              <div className="grid">
                <div className="c-full">
                  <button type="button" key="{index}" className="region-expand link f-r" onClick={toggleRegion}>{expandRegion ? 'Collapse all' : 'Expand all' }</button>
                  <ul className="country-list grid m-v-0">
                    {regions}
                  </ul>
                  <hr className="hr hr--light m-v-xxs"/>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ReactModal>
    </span>
  )
}

CountryFinderModal.propTypes = {
  modalIsOpen: PropTypes.bool,
  setIsOpen: PropTypes.func.isRequired,
  commodityCode: PropTypes.string,
  selectCountry: PropTypes.func,
}
CountryFinderModal.defaultProps = {
  modalIsOpen: false,
  commodityCode: '',
  selectCountry: null
}
