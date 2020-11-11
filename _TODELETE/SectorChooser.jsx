import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { slugify } from '../react-components/src/Helpers'
import Spinner from '../react-components/src/components/Spinner/Spinner'
import ErrorList from '../react-components/src/components/ErrorList'
import Sector from '../react-components/src/components/Sector'
import RecommendedCountries from './RecommendedCountries'

export default class SectorChooser extends React.Component {
  constructor(props) {
    super(props)
    const { selectedSectors, sectorList } = props

    this.state = {
      sectorList,
      selectedSectors,
      showSectorList: false,
      showTooltip: false,
      recommendedCountries: [],
      errors: [],
      isLoading: false,
    }

    this.hideSectorList = this.hideSectorList.bind(this)
    this.showSectorList = this.showSectorList.bind(this)
    this.handleMouseOver = this.handleMouseOver.bind(this)
    this.handleMouseOut = this.handleMouseOut.bind(this)
    this.fetchRecommendedCountries = this.fetchRecommendedCountries.bind(this)
    this.recommendedCountriesFetchSuccess = this.recommendedCountriesFetchSuccess.bind(this)
    this.removeSectorFetchSuccess = this.removeSectorFetchSuccess.bind(this)
    this.fetchError = this.fetchError.bind(this)
    this.retryRequest = this.retryRequest.bind(this)
  }

  componentDidMount() {
    const { selectedSectors } = this.state
    if (selectedSectors && selectedSectors.length) {
      this.fetchRecommendedCountries(selectedSectors)
    }
  }

  addRemoveSector = (sector) => {
    const { selectedSectors } = this.state
    if (selectedSectors.indexOf(sector) > -1) {
      this.removeSector(sector)
    } else {
      this.addSector(sector)
    }
  }

  addSector(sector) {
    const { selectedSectors } = this.state
    this.setState({
      selectedSectors: selectedSectors.concat([sector]),
    })
  }

  removeSector(sector) {
    const { selectedSectors } = this.state
    const updatedSectors = selectedSectors.filter((item) => item !== sector)

    if (updatedSectors.length === 0) {
      this.fetchRemoveSector()
    } else {
      this.fetchRecommendedCountries(updatedSectors)
    }
  }

  retryRequest() {
    const { selectedSectors } = this.state

    if (selectedSectors && selectedSectors.length) {
      this.fetchRecommendedCountries(selectedSectors)
    } else {
      this.fetchRemoveSector()
    }
  }

  fetchRecommendedCountries(sectors) {
    this.setState({ isLoading: true })

    Services.getCountriesDataBySectors(sectors)
      .then(this.recommendedCountriesFetchSuccess)
      .catch(this.fetchError)

    this.setState({ selectedSectors: sectors })
  }

  fetchRemoveSector() {
    this.setState({ isLoading: true })

    Services.removeSector()
      .then(this.removeSectorFetchSuccess)
      .catch(this.fetchError)
  }

  recommendedCountriesFetchSuccess(data) {
    this.setState({
      recommendedCountries: data.countries,
      isLoading: false,
      errors: [],
    })
  }

  removeSectorFetchSuccess() {
    this.setState({
      selectedSectors: [],
      recommendedCountries: [],
      isLoading: false,
      errors: [],
    })
  }

  fetchError(err) {
    this.setState({
      errors: err.__all__,
      isLoading: false,
    })
  }

  showSectorList() {
    this.setState({ showSectorList: true })
  }

  hideSectorList() {
    const { selectedSectors } = this.state
    this.setState({ showSectorList: false, showTooltip: false })
    this.fetchRecommendedCountries(selectedSectors)
  }

  handleMouseOver() {
    this.setState({ showTooltip: true })
  }

  handleMouseOut() {
    this.setState({ showTooltip: false })
  }

  render() {
    const {
      showSectorList,
      selectedSectors,
      sectorList,
      showTooltip,
      recommendedCountries,
      isLoading,
      errors,
    } = this.state

    const { addCountry, removeCountry, selectedCountries } = this.props

    let sectorListDisplay
    if (showSectorList) {
      sectorListDisplay = (
        <ul className="sector-list" id="sector-list">
          {sectorList.map((sector) => (
            <Sector
              name={sector}
              selected={selectedSectors.indexOf(sector) > -1}
              key={sector}
              id={slugify(sector)}
              handleSectorButtonClick={this.addRemoveSector}
            />
          ))}
        </ul>
      )
    }

    let sectorChooserButton
    if (!showSectorList) {
      sectorChooserButton = (
        <div className="sector-chooser-button">
          <button
            id="sector-chooser-button"
            type="button"
            className="icon--plus"
            onClick={this.showSectorList}
            onMouseOver={this.handleMouseOver}
            onFocus={this.handleMouseOver}
            onMouseOut={this.handleMouseOut}
            onBlur={this.handleMouseOut}
            aria-labelledby="sector-list-tooltip"
          />
          <div
            aria-hidden={!showTooltip}
            id="sector-list-tooltip"
            className={`sector-list-tooltip ${showTooltip ? '' : 'hidden'}`}
            role="tooltip"
          >
            Add sectors
          </div>
        </div>
      )
    }

    let saveButton
    if (selectedSectors && selectedSectors.length && showSectorList) {
      saveButton = (
        <button type="button" className="g-button m-t-0" id="sector-list-save" onClick={this.hideSectorList}>
          Save
        </button>
      )
    }

    let selectedSectorsDisplay
    if (selectedSectors && selectedSectors.length && !showSectorList) {

      selectedSectorsDisplay = (
        <>
          <p className="m-t-0 m-r-xs" id="sector-list-label">
            My sectors
          </p>
          <ul className="sector-list" id="selected-sectors" aria-labelledby="sector-list-label">
            {
              selectedSectors.map((sector) => (
                <Sector
                  name={sector}
                  selected={selectedSectors.indexOf(sector) !== -1}
                  key={sector}
                  id={slugify(sector)}
                  handleSectorButtonClick={this.addRemoveSector}
                />
              ))
            }
          </ul>
        </>
      )
    }

    let recommendedCountriesView
    if (isLoading) {
      recommendedCountriesView = <Spinner />
    } else if (recommendedCountries) {
      recommendedCountriesView = (
        <RecommendedCountries
          selectedCountries={selectedCountries}
          removeCountry={removeCountry}
          addCountry={addCountry}
          countries={recommendedCountries}
        />
      )
    } else {
      recommendedCountriesView = ''
    }

    let errorList
    if (errors && errors.length) {
      errorList = (
        <>
        <ErrorList errors={errors} />
        <button type="button" className="g-button" id="recommended-countries-retry" onClick={this.retryRequest}>
          Retry
        </button>
        </>
      )
    }

    return (
      <div id="recommended-countries" className="recommended-countries">
        <h2 className="h-m">Recommended countries</h2>
        <div id="sector-chooser" className="sector-chooser">
          <p className="m-t-0 intro-text">Add sectors you&apos;re interested in so we can recommend some countries.</p>
          {sectorListDisplay}
          {saveButton}
          {selectedSectorsDisplay}
          {sectorChooserButton}
        </div>
        {errorList}
        {recommendedCountriesView}
      </div>
    )
  }
}

SectorChooser.propTypes = {
  sectorList: PropTypes.arrayOf(PropTypes.string).isRequired,
  selectedSectors: PropTypes.arrayOf(PropTypes.string).isRequired,
  addCountry: PropTypes.func.isRequired,
  removeCountry: PropTypes.func.isRequired,
  selectedCountries: PropTypes.arrayOf(
    PropTypes.shape({
      country: PropTypes.string,
    }).isRequired
  ).isRequired,
}
