import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../Helpers'
import RecommendedCountry from './RecommendedCountry/RecommendedCountry'

export default class RecommendedCountries extends React.Component {
  constructor(props) {
    super(props)
    this.countryRef = React.createRef()
  }

  render() {
    const { countries } = this.props

    return (
      <ul className="grid" id="recommended-countries-list" ref={this.countryRef}>
        {countries.map((countryData) => (
          <li className="c-1-3" key={slugify(countryData.country)}>
            <RecommendedCountry countryData={countryData} />
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
      image: PropTypes.string.isRequired,
      selected: PropTypes.bool.isRequired,
    })
  ).isRequired,
}
