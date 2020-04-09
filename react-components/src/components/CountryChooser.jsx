import React from 'react'
import PropTypes from 'prop-types'
import Select from 'react-select'
import ErrorList from '@src/components/ErrorList'
import CountryData from '@src/components/CountryData'
import Services from '../Services'
import { slugify } from '../Helpers'
import './stylesheets/CountryChooser.scss'

export default class CountryChooser extends React.Component {
  constructor(props) {
    super(props)

    const { selectedCountries } = this.props

    const updatedSelectedCountryList = this.sanitizeSelectedCountries(selectedCountries)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountryList)

    this.state = {
      open: false,
      loading: false,
      selectedCountries: updatedSelectedCountryList,
      selectedCountry: null,
      countryList: updatedCountryList,
      errors: {},
    }

    this.showCountrySelect = this.showCountrySelect.bind(this)
    this.addCountry = this.addCountry.bind(this)
    this.handleGetCountryDataSuccess = this.handleGetCountryDataSuccess.bind(this)
    this.handleGetCountryDataError = this.handleGetCountryDataError.bind(this)
  }

  removeCountry = (country) => {
    const { selectedCountries } = this.state
    const updatedSelectedCountries = selectedCountries.filter((item) => item !== country)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountries)
    this.setState({ selectedCountries: updatedSelectedCountries, countryList: updatedCountryList })
    return false
  }

  changeCountry = (country) => {
    this.setState({ selectedCountry: country })
  }

  sanitizeSelectedCountries = (array) => {
    return array.filter((country) => country.export_duty !== undefined)
  }

  updatedCountryList = (selectedCountries) => {
    const { countryList } = this.props
    return countryList.filter(
      (country) => selectedCountries.filter((selectedCountry) => selectedCountry.country === country.value).length === 0
    )
  }

  addCountry() {
    const { selectedCountry, selectedCountries } = this.state
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

  showCountrySelect() {
    const { open } = this.state
    this.setState({ open: !open })
  }

  render() {
    const { selectedCountry, loading, open, selectedCountries, errors } = this.state
    const { countryList } = this.state
    let saveButton
    if (selectedCountry) {
      saveButton = (
        <button
          type="button"
          className="country-chooser-save-button"
          id="country-chooser-save-button"
          onClick={this.addCountry}
          disabled={loading}
        >
          Add
        </button>
      )
    }

    let countryInput
    if (open) {
      countryInput = (
        <>
          <div className="country-autocomplete-container m-t-s">
            <Select
              id="country-autocomplete"
              options={countryList}
              isMulti={false}
              isClearable
              disabled={loading}
              name="country"
              value={selectedCountry}
              onChange={this.changeCountry}
              autoFocus
              className="country-autocomplete"
              classNamePrefix="country-autocomplete"
              placeholder="Start typing a country name"
            />
            {saveButton}
          </div>
        </>
      )
    }

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
      <div className="country-chooser-section" id="country-chooser-section">
        {selectedCountries.map((country) => (
          <CountryData data={country} key={slugify(country.country)} removeCountry={this.removeCountry} />
        ))}
        {loadingMessage}
        <div>
          <ErrorList errors={errors.__all__ || []} className="m-v-s" />
        </div>
        <div className={`country-chooser ${open ? 'open' : ''}`}>
          <span className="button--plus" />
          <button
            type="button"
            className="country-chooser-button text-grey bg-stone-90 font-brand bg-hover-stone border-hover-stone pill"
            id="country-chooser-button"
            onClick={this.showCountrySelect}
          >
            Add a country
          </button>
          {countryInput}
        </div>
      </div>
    )
  }
}

CountryChooser.propTypes = {
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
}
