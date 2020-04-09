import React from 'react'
import PropTypes from 'prop-types'
import './RecommendedCountry.scss'
import { slugify } from '../../Helpers'
import Figure from '../Figure/Figure'

export default class RecommendedCountry extends React.Component {
  constructor(props) {
    super(props)

    const { selected } = this.props

    this.state = {
      selected,
    }

    this.handleClick = this.handleClick.bind(this)
  }

  handleClick(selectedCountry) {
    const { selected } = this.state
    const { addCountry } = this.props
    this.setState({ selected: !selected })

    addCountry(selectedCountry)
  }

  render() {
    const { countryData } = this.props
    const { selected } = this.state
    return (
      <button
        type="button"
        className={`recommended-country ${selected ? 'recommended-country--selected' : ''}`}
        aria-pressed={selected}
        id={slugify(countryData.country)}
        onClick={() => this.handleClick({ value: countryData.country, label: countryData.country })}
      >
        <Figure image={countryData.image} caption={countryData.country} />

        <div className="recommended-country__text">{selected ? 'Selected' : 'Select'}</div>
      </button>
    )
  }
}

RecommendedCountry.propTypes = {
  countryData: PropTypes.shape({
    country: PropTypes.string.isRequired,
    image: PropTypes.string.isRequired,
    selected: PropTypes.bool.isRequired,
  }).isRequired,
  addCountry: PropTypes.func.isRequired,
  selected: PropTypes.bool.isRequired,
}
