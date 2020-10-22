import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import RegionToggle from './RegionToggle'
import Confirmation from './MessageConfirmation'


const suggested = [{'country':'France', 'region':'Europe'}, {'country': 'Spain', 'region':'Europe'}, {'country':'Italy', 'region':'Europe'}, {'country':'Jamaica',  'region':'Latin America and Caribbean'}]

export function CountryFinderModal(props) {
  let scrollOuter
  const { modalIsOpen, setIsOpen, text, addButton } = props
  const [countryList, setCountryList] = useState()
  const [isScrolled, setIsScrolled] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState(text)
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

  const searchChange = (evt) => {
    setExpandRegion(evt.target.value.length > 0)
    setSearchStr(evt.target.value.toUpperCase())
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
    if (!countryList) {
      getCountries()
    }
  }

  const saveCountry = (country) => {
    setSelectedCountry(country.name)

    Services.updateExportPlan({
      export_countries: [
        {
          country_name: country.name,
          country_iso2_code: country.id,
          region: country.region
        }
      ]
    })
      .then(() => {
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

  let regions = Object.keys(countryList || {}).sort().map((region) => {
    const countries = (countryList[region] || []).map((country) => {
      if ((searchStr && country.name.toUpperCase().indexOf(searchStr) !== 0) || !region) return ''
      return (
        <span className="c-1-5" key={country.id}>
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
        <RegionToggle key={region} expandAllRegions={expandRegion} region={region} countries={countries} />
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
  const scrollerClass = `scroll-area ${isScrolled && isScrolled.top ? 'scroll-shadow-top' : ''} ${isScrolled && isScrolled.bottom ? 'scroll-shadow-bottom' : ''}`

  return (
    <span>
      { addButton &&
        <button type="button" className={buttonClass} onClick={openModal}>
          {selectedCountry || 'add country'}
          <i className={`fa ${(selectedCountry ? 'fa-edit' : 'fa-plus')}`}/>
        </button>
      }
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
          }
        }}
      >
        <form className="country-finder">
          <div className={`scroll-area m-t-0 ${scrollerClass}`} onScroll={onScroll}>
                <button type="button" className="f-r m-r-0 dialog-close" aria-label="Close" onClick={closeModal}/>
            <div 
              className="scroll-inner scroll-inner p-f-l p-r-l p-b-l p-t-xxs"
              ref={(_scrollInner) => {scrollOuter = _scrollInner || scrollOuter}}
            >
              <div>
                <h2 className="h-l m-t-s p-b-xs">Choose a target market</h2>
              </div>
              <h3 className="h-s">Suggested markets</h3>
              <p className="m-v-xs">
                These are based on the size of the market for your product, export distance, tariffs and costs.
              </p>
              <ul className="m-v-xs">
                {suggestedList}
              </ul>
              <hr className="bg-red-deep-100"/>
              <h3 className="h-s p-t-xs">Compare markets</h3>
              <div className="grid">
                <div className="c-full">
                  <p className="m-v-xs">Compare stats for over 180 markets to find the best place to target your exports.</p>
                  <button type="button" className="button button--tertiary" disabled>
                    Coming soon
                  </button>
                </div>
              </div>

              <hr className="bg-red-deep-100"/>
              <h3 className="h-s p-t-xs">List of markets</h3>
              <p className="m-v-xs">
                If you have an idea of where you want to export, choose from the list below. <br/>You can change this at any
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
                  />
                  <span className="visually-hidden">Search markets </span>
                  <i className="fas fa-search"/>

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

CountryFinderModal.propTypes = {
  addButton: PropTypes.bool,
  modalIsOpen: PropTypes.bool,
  setIsOpen: PropTypes.func.isRequired,
  text: PropTypes.string
}
CountryFinderModal.defaultProps = {
  addButton: true,
  modalIsOpen: false,
  text: '',
}

export const CountryFinder = ({ text }) => {

  const [modalIsOpen, setIsOpen] = useState(false)

  return (
    <span>
      <CountryFinderModal
        text={text}
        modalIsOpen={modalIsOpen}
        setIsOpen={setIsOpen}
      />
    </span>
  )
}

CountryFinder.propTypes = {
  text: PropTypes.string,
}
CountryFinder.defaultProps = {
  text: '',
}

export default function createCountryFinder({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  const text = params.element.getAttribute('data-text')
  ReactDOM.render(<CountryFinder text={text}/>, params.element)
}
