import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import Select from 'react-select'

import { slugify } from '../Helpers'
import Services from '../Services'
import ErrorList from '@src/components/ErrorList'
import CountryData from '@src/components/CountryData'

import './stylesheets/CountryChooser.scss'

const element = document.getElementById('country-chooser-section')

class CountryChooser extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      open: false,
      loading: false,
      selectedCountries: [],
      selectedCountry: null,
      data: null,
      errors: {},
    }
    this.showCountrySelect = this.showCountrySelect.bind(this)
    this.addCountry = this.addCountry.bind(this)
    this.handleGetCountryDataSuccess = this.handleGetCountryDataSuccess.bind(this)
    this.handleGetCountryDataError = this.handleGetCountryDataError.bind(this)
  }

  addCountry() {
    this.setState({
      loading: true,
      errors: {},
    })

    Services.getCountryData(this.state.selectedCountry.label)
    .then(this.handleGetCountryDataSuccess)
    .catch(this.handleGetCountryDataError)
  }

  removeCountry = country => {
    const updatedSelectedCountries = this.state.selectedCountries.filter(item => item != country)
    this.setState({selectedCountries: updatedSelectedCountries})
    return false
  }

  handleGetCountryDataSuccess(data) {
    this.setState({
      errors: {},
      loading: false,
      selectedCountries: this.state.selectedCountries.concat([data])
    })
  }

  handleGetCountryDataError(errors) {
    this.setState({
      errors: errors.message || errors,
      loading: false
    })
  }

  showCountrySelect() {
    this.state.open ? this.setState({open: false}) : this.setState({open: true})
  }

  changeCountry = country => {
    this.setState({selectedCountry: country})
  }

  render() {
    let saveButton
    if (this.state.selectedCountry) {
      saveButton = (
        <button
          className='country-chooser-save-button'
          id='country-chooser-save-button'
          onClick={this.addCountry}
          disabled={this.state.loading}
          >Add</button>
      )
    }

    let countryInput
    if (this.state.open) {
      countryInput = (
        <>
          <div className='country-autocomplete-container m-t-s'>
            <Select
              id='country-autocomplete'
              options={this.props.countryList}
              isMulti={false}
              isClearable={true}
              disabled={this.state.loading}
              name='country'
              value={this.state.selectedCountry}
              onChange={this.changeCountry}
              autoFocus={true}
              className='country-autocomplete'
              classNamePrefix='country-autocomplete'
              placeholder='Start typing a country name'
            />
          {saveButton}
        </div>
      </>
      )
    }

    let loadingMessage
    if (this.state.loading) {
      loadingMessage = (
        <p className='loading-message'>Fetching country data<span>.</span><span>.</span><span>.</span></p>
      )
    }

    return (
      <>
      {
        this.state.selectedCountries.map(country =>
          <CountryData
            data={country}
            key={country.name}
            removeCountry={this.removeCountry} />
        )
      }
      {loadingMessage}
      <div>
        <ErrorList errors={this.state.errors.__all__ || []} className='m-v-s' />
      </div>
      <div className={`country-chooser ${this.state.open ? 'open' : ''}`}>
        <span className='button--plus'></span>
        <button
          className='country-chooser-button text-grey bg-stone-90 font-brand bg-hover-stone border-hover-stone pill'
          id='country-chooser-button' onClick={this.showCountrySelect}>
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
  countryList: PropTypes.array.isRequired
}

CountryChooser.defaultProps = {
  countryList: [],
}

export {
  CountryChooser,
  createCountryChooser,
}
