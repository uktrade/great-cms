import React from 'react'
import PropTypes from 'prop-types'
import './RecommendedCountry.scss'
import { slugify } from '../../Helpers'
import Figure from '../Figure/Figure'

export default class RecommendedCountry extends React.Component {
  constructor(props) {
    super(props)

    const { countryData } = this.props

    this.state = {
      selected: countryData.selected,
    }

    this.handleClick = this.handleClick.bind(this)
  }

  handleClick() {
    const { selected } = this.state
    this.setState({ selected: !selected })

    /* 
        axios.get(`/load-country?country=${this.props.country.id}`)
            .then(data => { })
            .catch(error => { });
        */

    // dispatch event with country name to be fetch by Country stat section component?
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
        onClick={this.handleClick}
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
}
