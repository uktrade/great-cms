import React, { useState, useEffect } from 'react'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useSuggestedMarkets } from '@src/components/hooks/useSuggestedMarkets'
import RegionToggle from './RegionToggle'
import SearchInput from './SearchInput'
import { analytics } from '../../Helpers'

export default function CountryFinderModal(props) {
  let scrollOuter
  const {
    modalIsOpen,
    setIsOpen,
    activeProducts,
    selectCountry,
    isCompareCountries,
    market,
    onCloseRedirect,
  } = props
  const [countryList, setCountryList] = useState()
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchStr, setSearchStr] = useState()
  const [expandRegion, setExpandRegion] = useState(false)
  const [mobilePage, setMobilePage] = useState('initial')
  const { suggestedCountries, loadSuggestedCountries } = useSuggestedMarkets(
    activeProducts
  )

  useEffect(() => {
    if (modalIsOpen) {
      analytics({
        event: 'addMarketPageview',
        virtualPageUrl: '/choose-target-market-modal',
        virtualPageTitle: 'Choose Target Market Modal',
      })
    }
  }, [modalIsOpen])

  const closeModal = () => {
    setSearchStr('')
    setExpandRegion(false)
    setIsOpen(false)
    setMobilePage('initial')
    if (onCloseRedirect && !market.country_name) {
      window.location.href = onCloseRedirect
    }
  }

  const setScrollShadow = () => {
    if (scrollOuter) {
      const bottomOverflow =
        scrollOuter.scrollHeight -
        (scrollOuter.scrollTop + scrollOuter.clientHeight)
      setIsScrolled({
        top: scrollOuter.scrollTop > 0,
        bottom: bottomOverflow > 0,
      })
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

  const getCountries = () => {
    Services.getCountries().then((result) => {
      // map regions
      const regions = {}
      result.map((country) => {
        const { region } = country
        ;(regions[region] = regions[region] || []).push(country)
        return null
      })
      setCountryList(regions)
    })
  }

  useEffect(() => {
    if (modalIsOpen) {
      loadSuggestedCountries()
    }
  }, [activeProducts, modalIsOpen])

  const modalAfterOpen = () => {
    if (!countryList) {
      getCountries()
    }
  }

  const clickCountry = (evt) => {
    const button = evt.target.closest('button')
    const country = {
      country_name: button.getAttribute('data-country'),
      country_iso2_code: button.getAttribute('data-id'),
      region: button.getAttribute('data-region'),
      suggested: button.getAttribute('data-suggested'),
    }
    if (!isCompareCountries) {
      analytics({
        event: 'addMarketSuccess',
        suggestMarket: country.suggested ? country.country_name : '',
        listMarket: country.suggested ? '' : country.country_name,
      })
    }
    selectCountry(country)
    closeModal()
  }

  let regions = Object.keys(countryList || {})
    .sort()
    .map((region, index) => {
      const countries = (countryList[region] || []).map((country) => {
        if (
          (searchStr && country.name.toUpperCase().indexOf(searchStr) !== 0) ||
          !region
        )
          return ''
        return (
          <li className="c-1-5" key={`country-${country.id}`}>
            <button
              type="button"
              className="link m-r-s m-b-xs"
              data-country={country.name}
              data-id={country.id}
              data-region={country.region}
              onClick={clickCountry}
            >
              {country.name}
            </button>
          </li>
        )
      })
      return (
        !!countries.filter((countryRegion) => countryRegion).length && (
          <RegionToggle
            key={region}
            expandAllRegions={expandRegion}
            region={region}
            countries={countries}
            index={index}
          />
        )
      )
    })

  if (!regions.filter((region) => region).length) {
    regions = <div className="h-xs">No results found</div>
  }

  /*   Suggested markets section  */
  let suggestedSection = (
    <div>
      <h3 className="h-s">Possible export markets</h3>
      <p className="m-v-xs">
        Add a product so that we can suggest export markets.
      </p>
    </div>
  )
  if (suggestedCountries && suggestedCountries.suggestions) {
    const suggestedList = suggestedCountries.suggestions.map((country) => {
      return (
        <button
          key={`suggested_${country.country_iso2}`}
          type="button"
          className="tag tag--tertiary tag--icon m-r-s m-v-xxs"
          data-country={country.country_name}
          data-region={country.region}
          data-id={country.country_iso2}
          onClick={clickCountry}
          data-suggested
        >
          {country.country_name}
          <i className="fa fa-plus" />
        </button>
      )
    })
    suggestedSection = (
      <div className="suggested-markets">
        <h3 className="h-s">Possible export markets</h3>
        <div className="m-v-xs">{suggestedList}</div>
        <p className="m-v-xs">
          These markets are based on consumer demand, export distance, tariffs
          and costs for exporting{' '}
          <span className="body-l-b">
            {suggestedCountries.hs2Desc.toLowerCase()}
          </span>{' '}
          from the UK. This is an HS2 category that includes{' '}
          <span className="body-l-b">
            {suggestedCountries.details.product.toLowerCase()} (HS code{' '}
            {suggestedCountries.details.hs6})
          </span>
          , along with other products categorised at an HS4 and HS6 level. For
          more information on HS codes see our{' '}
          <a href="/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/get-your-goods-into-the-destination-country/using-commodity-codes/">
            lesson on using HS codes
          </a>
          .
        </p>

      </div>
    )
  }
  /*   Compare markets section  */
  const compareMarketsSection = (
    <div>
      <h3 className="h-s p-t-xs">Where to export</h3>
      <div className="grid">
        <div className="c-full">
          <p className="m-v-xs">
            Compare data for different markets to make an informed choice about
            where to export.
          </p>
          <a href="/where-to-export/" className="button button--secondary">
            Compare markets
          </a>
        </div>
      </div>
    </div>
  )

  /* Filtered list of places */
  const marketListSection = (
    <div>
      <h3 className="h-s p-t-xs">
        <label htmlFor="search-input">Countries and territories</label>
      </h3>
      <p id="search-hint" className="m-v-xs">
        If you already have an idea of where you want to export to, choose from
        this list.
      </p>
      <div className="grid">
        <div className="c-1-3 m-b-xxs">
          <SearchInput
            id="search-input"
            onChange={searchChange}
            iconClass="fa-search"
            placeholder="Search markets"
            ariaDescribedby="search-hint"
          />
        </div>
      </div>
      <div className="grid">
        <div className="c-full clearfix">
          <button
            type="button"
            key="{index}"
            className="region-expand link f-r"
            onClick={toggleRegion}
          >
            {expandRegion ? 'Collapse all' : 'Expand all'}
          </button>
        </div>
        <div className="c-full">
          <div className="country-list grid m-v-0">{regions}</div>
          <hr className="hr hr--light m-v-xxs" />
        </div>
      </div>
    </div>
  )

  const mobileSection = {
    initial: (
      <div className="only-mobile">
        <div>
          <h2 className="h-l m-t-s p-b-xs">
            {!isCompareCountries
              ? 'Choose a market'
              : 'Choose a market to compare'}
          </h2>
        </div>
        <p>
          {!isCompareCountries
            ? 'There are 3 ways to choose a target export market'
            : 'There are 2 ways to choose a market to compare'}
        </p>
        <button
          type="button"
          className="button button--secondary button--full-width m-b-s"
          onClick={() => setMobilePage('suggested')}
        >
          Possible export markets
        </button>
        {!isCompareCountries && (
          <button
            type="button"
            className="button button--secondary button--full-width m-b-s"
            onClick={() => setMobilePage('compare')}
          >
            Compare markets
          </button>
        )}
        <button
          type="button"
          className="button button--secondary button--full-width m-b-s"
          onClick={() => setMobilePage('list')}
        >
          List of markets
        </button>
      </div>
    ),
    suggested: suggestedSection,
    compare: compareMarketsSection,
    list: marketListSection,
  }

  const scrollerClass = `scroll-area ${
    isScrolled && isScrolled.top ? 'scroll-shadow-top' : ''
  } ${isScrolled && isScrolled.bottom ? 'scroll-shadow-bottom' : ''}`

  return (
    <span>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        className="modal large-modal-content"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
      >
        <div className="country-finder text-blue-deep-80">
          <div
            className={`scroll-area m-t-0 ${scrollerClass}`}
            onScroll={onScroll}
          >
            <button
              type="button"
              className="f-r m-r-0 dialog-close"
              aria-label="Close"
              onClick={closeModal}
            />
            <div
              className="scroll-inner scroll-inner p-f-l p-r-l p-b-l p-t-xxs"
              ref={(_scrollInner) => {
                scrollOuter = _scrollInner || scrollOuter
              }}
            >
              {/* Desktop rendering with all sections available */}
              <div className="only-desktop">
                <div>
                  <h2 className="h-l m-t-s p-b-xs">Choose a market</h2>
                </div>
                {suggestedSection}
                <hr className="hr bg-red-deep-100" />
                {!isCompareCountries && (
                  <>
                    {compareMarketsSection}
                    <hr className="hr bg-red-deep-100" />
                  </>
                )}
                {marketListSection}
              </div>
              {/* Mobile section rendering with buttons to choose which section to show */}
              <div className="only-mobile">
                <button
                  type="button"
                  className={`pull-left m-t-s button button--secondary button--icon button--auto-width ${
                    mobilePage === 'initial' ? 'hidden' : ''
                  }`}
                  onClick={() => setMobilePage('initial')}
                >
                  <i className="fa fa-arrow-left" />
                  Back
                </button>
                {mobileSection[mobilePage]}
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
  activeProducts: PropTypes.arrayOf(
    PropTypes.shape({
      commodity_code: PropTypes.string,
      commodity_name: PropTypes.string,
    })
  ),
  selectCountry: PropTypes.func.isRequired,
  isCompareCountries: PropTypes.bool,
  onCloseRedirect: PropTypes.string,
  market: PropTypes.shape({
    country_name: PropTypes.string,
    country_iso2_code: PropTypes.string,
    region: PropTypes.string,
  }),
}
CountryFinderModal.defaultProps = {
  modalIsOpen: false,
  activeProducts: null,
  isCompareCountries: false,
  onCloseRedirect: '',
  market: {},
}
