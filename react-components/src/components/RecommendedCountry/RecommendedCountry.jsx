import React from 'react'
import PropTypes from 'prop-types'
import './RecommendedCountry.scss'
import { slugify } from '../../Helpers'
import Figure from '../Figure/Figure'

export default class RecommendedCountry extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      isFetching: false,
    }

    this.handleClick.bind(this)
  }

  componentDidUpdate(props) {
    const { selected } = this.props

    if (selected !== props.selected) {
      this.removeFetching()
    }
  }

  removeFetching() {
    this.setState({
      isFetching: false,
    })
  }

  handleClick(selectedCountry) {
    const { addCountry, removeCountry, selected } = this.props
    this.setState({
      isFetching: true,
    })

    if (selected) {
      removeCountry({ country: selectedCountry.value })
    } else {
      addCountry(selectedCountry)
    }
  }

  render() {
    const { isFetching } = this.state
    const { countryData, selected } = this.props
    const id = slugify(countryData.country)
    const imgUrl = `/static/images/country/${id}.png` // ideally this should be comming from personalisation API

    let countryText
    if (isFetching && !selected) {
      countryText = 'Selecting'
    } else if (isFetching && selected) {
      countryText = 'Unselecting'
    } else if (selected) {
      countryText = 'Selected'
    } else {
      countryText = 'Select'
    }

    return (
      <button
        type="button"
        className={`recommended-country ${selected ? 'recommended-country--selected' : ''}`}
        aria-pressed={selected}
        id={id}
        onClick={() => this.handleClick({ value: countryData.country, label: countryData.country })}
      >
        <Figure image={imgUrl} caption={countryData.country} />

        <div className="recommended-country__text">{countryText}</div>
      </button>
    )
  }
}

RecommendedCountry.propTypes = {
  countryData: PropTypes.shape({
    country: PropTypes.string.isRequired,
  }).isRequired,
  addCountry: PropTypes.func.isRequired,
  removeCountry: PropTypes.func.isRequired,
  selected: PropTypes.bool.isRequired,
}
