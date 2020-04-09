import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import SectorChooser from './SectorChooser'
import CountryChooser from './CountryChooser'

class TargetMarketCountries extends React.Component {
  constructor(props) {
    super(props)

    this.state = {}
  }

  render() {
    const { selectedSectors, sectorList, selectedCountries, countryList } = this.props
    return (
      <>
        <SectorChooser selectedSectors={selectedSectors} sectorList={sectorList} />
        <CountryChooser selectedCountries={selectedCountries} countryList={countryList} />
      </>
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
