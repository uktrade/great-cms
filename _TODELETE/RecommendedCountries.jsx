import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../react-components/src/Helpers'
import RecommendedCountry from './RecommendedCountry/RecommendedCountry'

export default class RecommendedCountries extends React.Component {
  constructor(props) {
    super(props)
    this.countryRef = React.createRef()
  }

  isSelectedAlready(countryName) {
    const { selectedCountries } = this.props

    return selectedCountries.filter((country) => country.country === countryName).length > 0
  }

  render() {
    const { countries, addCountry, removeCountry } = this.props

    return (
      <ul className="grid m-t-0" id="recommended-countries-list" ref={this.countryRef}>
        {countries.map((countryData) => (
          <li className="c-1-3" key={slugify(countryData.country)}>
            <RecommendedCountry
              selected={this.isSelectedAlready(countryData.country)}
              addCountry={addCountry}
              removeCountry={removeCountry}
              countryData={countryData}
            />
          </li>
        ))}
      </ul>
    )
  }
}

RecommendedCountries.propTypes = {
  countries: PropTypes.arrayOf(
    PropTypes.shape({
      country: PropTypes.string.isRequired,
    })
  ).isRequired,
  addCountry: PropTypes.func.isRequired,
  removeCountry: PropTypes.func.isRequired,
  selectedCountries: PropTypes.arrayOf(
    PropTypes.shape({
      country: PropTypes.string,
    }).isRequired
  ).isRequired,
}
