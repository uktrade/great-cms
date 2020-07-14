import React from 'react'
import PropTypes from 'prop-types'
import Select from 'react-select'
import './stylesheets/CountryChooser.scss'

export default class CountryChooser extends React.Component {
  constructor(props) {
    super(props)

    const { countryList } = this.props

    this.state = {
      open: false,
      selectedCountry: null,
      countryList,
    }

    this.showCountrySelect = this.showCountrySelect.bind(this)
  }

  componentDidUpdate(newProps) {
    const { countryList } = this.state
    if (newProps.countryList !== countryList) {
      this.updateCountryList(newProps.countryList)
      this.changeCountry(null)
    }
  }

  changeCountry = (country) => {
    this.setState({ selectedCountry: country })
  }

  updateCountryList(list) {
    this.setState({
      countryList: list,
    })
  }

  showCountrySelect() {
    const { open } = this.state
    this.setState({ open: !open })
  }

  render() {
    const { selectedCountry, loading, open, countryList } = this.state
    const { addCountry } = this.props

    let saveButton
    if (selectedCountry) {
      saveButton = (
        <button
          type="button"
          className="country-chooser-save-button"
          id="country-chooser-save-button"
          onClick={() => addCountry(selectedCountry)}
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

    return (
      <div className="country-chooser-section" id="country-chooser-section">
        <div className={`button--plus ${open ? 'open' : ''}`}>
          <span className="icon--plus" />
          <button
            type="button"
            className="button--stone"
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
  countryList: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  addCountry: PropTypes.func.isRequired,
}
