import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import CountryData from '@src/components/CountryData'
import ErrorList from '@src/components/ErrorList'
import SectorChooser from './SectorChooser'
import CountryChooser from './CountryChooser'
import { slugify } from '../Helpers'
import Services from '../Services'

class TargetMarketCountries extends React.Component {
  constructor(props) {
    super(props)

    const { selectedCountries } = this.props
    const updatedSelectedCountryList = this.sanitizeSelectedCountries(selectedCountries)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountryList)

    this.state = {
      countryList: updatedCountryList,
      selectedCountries: updatedSelectedCountryList,
      errors: {},
      loading: false,
    }

    this.addCountry = this.addCountry.bind(this)
    this.removeCountry = this.removeCountry.bind(this)
    this.handleGetCountryDataSuccess = this.handleGetCountryDataSuccess.bind(this)
    this.handleGetCountryDataError = this.handleGetCountryDataError.bind(this)
  }

  /**
   * Ensures the list for country chooser does not have countries that are already selected
   */
  updatedCountryList = (selectedCountries) => {
    const { countryList } = this.props
    return countryList.filter(
      (country) => selectedCountries.filter((selectedCountry) => selectedCountry.country === country.value).length === 0
    )
  }

  // This fucntion should be removed when BE fixes returning multiple duplicate countries without data
  sanitizeSelectedCountries = (array) => {
    return array.filter((country) => country.export_duty !== undefined)
  }

  removeCountry(data) {
    const { selectedCountries } = this.state
    const updatedSelectedCountries = selectedCountries.filter((item) => item.country !== data.country)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountries)
    this.setState({ selectedCountries: updatedSelectedCountries, countryList: updatedCountryList })
    Services.removeCountryData(data.country)
       .then(this.handleGetCountryDataSuccess)
       .catch(this.handleGetCountryDataError)
  }

  addCountry(selectedCountry) {
    const { selectedCountries } = this.state
    const isExisting = selectedCountries.filter((country) => country.country === selectedCountry.value).length > 0

    if (!isExisting) {
      this.setState({
        loading: true,
        errors: {},
      })

      Services.getCountryData(selectedCountry.label)
        .then(this.handleGetCountryDataSuccess)
        .catch(this.handleGetCountryDataError)
    }
  }

  handleGetCountryDataSuccess(data) {
    // data should return only a single country
    // currently it returns the whole array of selected countries
    // TODO needs BE work
    const updatedSelectedCountryList = this.sanitizeSelectedCountries(data.target_markets)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountryList)

    this.setState({
      errors: {},
      loading: false,
      selectedCountries: updatedSelectedCountryList,
      countryList: updatedCountryList,
    })
  }

  handleGetCountryDataError(errors) {
    this.setState({
      errors: errors.message || errors,
      loading: false,
    })
  }

  render() {
    const { selectedSectors, sectorList } = this.props
    const { countryList, selectedCountries, errors, loading } = this.state

    let loadingMessage
    if (loading) {
      loadingMessage = (
        <p className="loading-message">
          Fetching country data
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </p>
      )
    }

    return (
      <div className="target-markets-section">
        <SectorChooser
          selectedCountries={selectedCountries}
          addCountry={this.addCountry}
          removeCountry={this.removeCountry}
          selectedSectors={selectedSectors}
          sectorList={sectorList}
        />
        <hr />
        {selectedCountries.map((country) => (
          <CountryData data={country} key={slugify(country.country)} removeCountry={this.removeCountry} />
        ))}
        {loadingMessage}
        <div>
          <ErrorList errors={errors.__all__ || []} className="m-v-s" />
        </div>
        <CountryChooser countryList={countryList} addCountry={this.addCountry} />
      </div>
    )
  }
}

function createTargetMarketCountries({ element, ...params }) {
  ReactDOM.render(<TargetMarketCountries {...params} />, element)
}

TargetMarketCountries.propTypes = {
  selectedCountries: PropTypes.arrayOf(
    PropTypes.shape({
      export_duty: PropTypes.number,
      country: PropTypes.string,
      commodity_name: PropTypes.string,
      utz_offset: PropTypes.string,
      timezone: PropTypes.string,
      last_year_data: PropTypes.shape({
        year: PropTypes.string,
        trade_value: PropTypes.string,
        country_name: PropTypes.string,
        year_on_year_change: PropTypes.string,
      }),
      corruption_perceptions_index: PropTypes.shape({
        rank: PropTypes.number,
        country_code: PropTypes.string,
        country_name: PropTypes.string,
        cpi_score_2019: PropTypes.number,
      }),
      easeofdoingbusiness: PropTypes.shape({
        total: PropTypes.number,
        year_2019: PropTypes.number,
        country_code: PropTypes.string,
        country_name: PropTypes.string,
      }),
    }).isRequired
  ).isRequired,
  countryList: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  sectorList: PropTypes.arrayOf(PropTypes.string).isRequired,
  selectedSectors: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export { TargetMarketCountries, createTargetMarketCountries }
