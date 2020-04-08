import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Select from 'react-select'
import ErrorList from '@src/components/ErrorList'
import CountryData from '@src/components/CountryData'
import Services from '../Services'
import { slugify } from '../Helpers'
import './stylesheets/CountryChooser.scss'

class CountryChooser extends React.Component {
  constructor(props) {
    super(props)

    const { selectedCountries } = this.props
    const updatedCountryList = this.updatedCountryList(selectedCountries)

    this.state = {
      open: false,
      loading: false,
      selectedCountries,
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

  updatedCountryList = (selectedCountries) => {
    const { countryList } = this.props
    return countryList.filter(
      (country) => selectedCountries.filter((selectedCountry) => selectedCountry.country === country.value).length === 0
    )
  }

  addCountry() {
    const { selectedCountry } = this.state
    this.setState({
      loading: true,
      errors: {},
    })

    Services.getCountryData(selectedCountry.label)
      .then(this.handleGetCountryDataSuccess)
      .catch(this.handleGetCountryDataError)
  }

  handleGetCountryDataSuccess(data) {
    const { selectedCountries } = this.state
    const updatedSelectedCountries = selectedCountries.concat(data.target_markets)
    const updatedCountryList = this.updatedCountryList(updatedSelectedCountries)

    this.setState({
      errors: {},
      loading: false,
      selectedCountries: updatedSelectedCountries,
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
      <>
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
      </>
    )
  }
}

function createCountryChooser({ element, ...params }) {
  ReactDOM.render(<CountryChooser {...params} />, element)
}

CountryChooser.propTypes = {
  selectedCountries: PropTypes.arrayOf(
    PropTypes.shape({
      export_duty: PropTypes.number.isRequired,
      country: PropTypes.string.isRequired,
      last_year_data: PropTypes.shape({
        year: PropTypes.string.isRequired,
        trade_value: PropTypes.string.isRequired,
        country_name: PropTypes.string.isRequired,
        year_on_year_change: PropTypes.string.isRequired,
      }),
      corruption_perceptions_index: PropTypes.shape({
        rank: PropTypes.number,
        country_code: PropTypes.string.isRequired,
        country_name: PropTypes.string.isRequired,
        cpi_score_2019: PropTypes.number.isRequired,
      }).isRequired,
      easeofdoingbusiness: PropTypes.shape({
        total: PropTypes.number.isRequired,
        year_2019: PropTypes.number,
        country_code: PropTypes.string.isRequired,
        country_name: PropTypes.string.isRequired,
      }).isRequired,
    }).isRequired
  ).isRequired,
  countryList: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
}

export { CountryChooser, createCountryChooser }
