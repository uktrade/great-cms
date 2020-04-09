import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { slugify } from '../Helpers'
import Spinner from './Spinner/Spinner'
import Sector from './Sector'
import RecommendedCountries from './RecommendedCountries'

export default class SectorChooser extends React.Component {
  constructor(props) {
    super(props)
    const { selectedSectors, sectorList } = props

    this.state = {
      sectorList,
      selectedSectors,
      savedSelectedSectors: selectedSectors,
      showSectorList: false,
      showTooltip: false,
      recommendedCountries: null,
      fetchError: null,
      isLoading: false,
    }

    this.showHideSectorList = this.showHideSectorList.bind(this)
    this.handleMouseOver = this.handleMouseOver.bind(this)
    this.handleMouseOut = this.handleMouseOut.bind(this)
    this.fetchRecommendedCountries = this.fetchRecommendedCountries.bind(this)
    this.recommendedCountriesFetchSuccess = this.recommendedCountriesFetchSuccess.bind(this)
    this.recommendedCountriesFetchError = this.recommendedCountriesFetchError.bind(this)
  }

  componentDidMount() {
    const { selectedSectors } = this.state
    if (selectedSectors && selectedSectors.length > 0) {
      this.fetchRecommendedCountries()
    }
  }

  handleSectorButtonClick = (sector) => {
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
    const updatedSelectedSectors = selectedSectors.filter((id) => id !== sector)
    this.setState({ selectedSectors: updatedSelectedSectors })

    if (updatedSelectedSectors && updatedSelectedSectors.length > 0) {
      this.fetchRecommendedCountries()
    } else {
      this.setState({
        recommendedCountries: null,
      })
    }
  }

  fetchRecommendedCountries() {
    const { selectedSectors } = this.state
    this.setState({
      savedSelectedSectors: selectedSectors,
      isLoading: true,
    })

    Services.getCountriesDataBySectors(selectedSectors)
      .then(this.recommendedCountriesFetchSuccess)
      .catch(this.recommendedCountriesFetchError)
  }

  recommendedCountriesFetchSuccess(data) {
    this.setState({
      recommendedCountries: data.countries,
      isLoading: false,
    })
  }

  recommendedCountriesFetchError(err) {
    this.setState({
      fetchError: err,
      isLoading: false,
    })
  }

  showHideSectorList() {
    const { showSectorList, selectedSectors, savedSelectedSectors } = this.state
    if (showSectorList) {
      this.setState({ showSectorList: false })
      const isEqual = selectedSectors.every((e) => savedSelectedSectors.includes(e))
      if (!isEqual) {
        this.fetchRecommendedCountries()
      }
    } else {
      this.setState({ showSectorList: true })
      this.setState({ showTooltip: false })
    }
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
      fetchError,
    } = this.state

    const { addCountry, selectedCountries } = this.props

    let sectorListDisplay
    if (showSectorList) {
      sectorListDisplay = (
        <ul className="sector-list" id="sector-list">
          {sectorList.map((sector) => (
            <Sector
              name={sector}
              selected={selectedSectors.indexOf(slugify(sector)) > -1}
              key={sector}
              id={slugify(sector)}
              handleSectorButtonClick={this.handleSectorButtonClick}
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
            className="button--plus"
            onClick={this.showHideSectorList}
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
    if (selectedSectors && selectedSectors.length > 0 && showSectorList) {
      saveButton = (
        <button type="button" className="g-button" onClick={this.showHideSectorList}>
          Save
        </button>
      )
    }

    let selectedSectorsDisplay
    if (selectedSectors && selectedSectors.length > 0 && !showSectorList) {
      const currentSelectedSectors = selectedSectors
      const sectors = currentSelectedSectors.map((sector) => (
        <Sector
          name={sector}
          selected={currentSelectedSectors.indexOf(slugify(sector)) !== -1}
          key={sector}
          id={slugify(sector)}
          handleSectorButtonClick={this.handleSectorButtonClick}
        />
      ))
      selectedSectorsDisplay = (
        <>
          <p className="m-t-0 m-r-xs" id="sector-list-label">
            My sectors
          </p>
          <ul className="sector-list" id="selected-sectors" aria-labelledby="sector-list-label">
            {sectors}
          </ul>
        </>
      )
    }

    let recommendedCountriesView
    if (isLoading) {
      recommendedCountriesView = <Spinner />
    } else if (recommendedCountries && !fetchError) {
      recommendedCountriesView = (
        <RecommendedCountries selectedCountries={selectedCountries} addCountry={addCountry} countries={recommendedCountries} />
      )
    } else if (fetchError) {
      recommendedCountriesView = 'Error fetching data.'
    } else {
      recommendedCountriesView = ''
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

        {recommendedCountriesView}
      </div>
    )
  }
}

SectorChooser.propTypes = {
  sectorList: PropTypes.arrayOf(PropTypes.string).isRequired,
  selectedSectors: PropTypes.arrayOf(PropTypes.string).isRequired,
  addCountry: PropTypes.func.isRequired,
  selectedCountries: PropTypes.arrayOf(
    PropTypes.shape({
      country: PropTypes.string,
    }).isRequired
  ).isRequired,
}
