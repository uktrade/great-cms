import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../Helpers'
import EducationalMomentTooltip from './EducationalMomentTooltip'

export default class CountryData extends React.Component {
  constructor(props) {
    super(props)
    const {
      data: { timezone },
    } = this.props
    this.state = {
      time: new Date().toLocaleTimeString('en-GB', { timeZone: timezone }), // has to come from data TODO
    }
    this.handleClick = this.handleClick.bind(this)
  }

  componentDidMount() {
    this.timerID = setInterval(() => {
      this.tick()
    }, 1000)
  }

  componentWillUnmount() {
    clearInterval(this.timerID)
  }

  tick() {
    const {
      data: { timezone },
    } = this.props
    this.setState({
      time: new Date().toLocaleTimeString('en-GB', { timeZone: timezone }),
    })
  }

  handleClick() {
    const { removeCountry, data } = this.props
    removeCountry(data)
  }

  render() {
    const {
      data: {
        utz_offset: utzOffset,
        timezone,
        commodity_name: commodityName,
        export_duty: exportDuty,
        country,
        last_year_data: lastYearData,
        corruption_perceptions_index: corruptionPerceptionsIndex,
        easeofdoingbusiness,
      },
    } = this.props

    const { time } = this.state
    const sectionID = `export-market-data--${slugify(country)}`
    const countryData = (
      <>
        <section id={sectionID}>
          <h2 className="h-l p-b-0 inline-block">{country}</h2>
          <button type="button" onClick={this.handleClick} className="remove-country-button">
            Remove <span className="visually-hidden">{country}</span>
          </button>
          <div className="flex-grid">
            <div className="c-1-3" id={`ease-of-doing-business-rank-${slugify(country)}`}>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption educational-moment__paragraph">Ease of doing business rank</p>
                  <EducationalMomentTooltip
                    id="ease-of-doing-business-tooltip"
                    heading="What is Ease of Doing Business Rank?"
                    description="Ease of doing business ranks economies from 1 to 190, with first place being the best. A high ranking (a low numerical rank) means that the regulatory environment is conducive to business operation"
                    />
                </figcaption>
                <p className="statistic__figure">
                  {easeofdoingbusiness && easeofdoingbusiness.year_2019 ? (
                    <>
                      {easeofdoingbusiness.year_2019}{' '}
                      <span className="statistic__details">out of {easeofdoingbusiness.total}</span>
                    </>
                  ) : (
                    'No data'
                  )}
                </p>
              </figure>
            </div>
            <div className="c-1-3" id={`corruption-perception-index-${slugify(country)}`}>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption educational-moment__paragraph">Corruption Perception Index</p>
                    <EducationalMomentTooltip
                      id="corruption-perception-index-tooltip"
                      heading="What is the Corruption Perception Index?"
                      description='The Corruption Perception Index (CPI) is an index published annually by Transparency International since 1995 which ranks countries "by their perceived levels of public sector corruption, as determined by expert assessments and options surveys."'
                      />
                </figcaption>
                <p className="statistic__figure">
                  {corruptionPerceptionsIndex && corruptionPerceptionsIndex.rank ? (
                    <>{corruptionPerceptionsIndex.rank}</>
                  ) : (
                    'No data'
                  )}
                </p>
              </figure>
            </div>
            <div className="c-1-3" id={`local-time-${slugify(country)}`}>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Local time</p>
                </figcaption>
                <p className="statistic__figure">
                  <time>{time}</time>
                  <span className="statistic__details">
                    GMT {utzOffset} {timezone}
                  </span>
                </p>
              </figure>
            </div>
          </div>
          <div className="flex-grid">
            <div className="c-1-3" id={`duty-${slugify(country)}`}>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Duty</p>
                </figcaption>
                <p className="statistic__figure">{exportDuty > 0 ? `${exportDuty}%` : 'No duty'}</p>
              </figure>
            </div>
            <div className="c-1-3" id={`import-value-${slugify(country)}`}>
              {lastYearData ? (
                <figure className="statistic">
                  <figcaption>
                    <p className="statistic__caption">
                      <span className="text-flag-red">{commodityName}</span> import value in {lastYearData.year}
                    </p>
                  </figcaption>
                  <p className="statistic__figure">
                    {parseInt(lastYearData.trade_value).toLocaleString()} USD <span className="statistic__details">Source: Comtrade</span>
                  </p>
                </figure>
              ) : null}
            </div>
            <div className="c-1-3" id={`year-to-year-change-${slugify(country)}`}>
              {lastYearData ? (
                <figure className="statistic">
                  <figcaption>
                    <p className="statistic__caption">Year-to-year change</p>
                  </figcaption>
                  <p className="statistic__figure">+{lastYearData.year_on_year_change}%</p>
                </figure>
              ) : null}
            </div>
          </div>
        </section>
        <hr />
      </>
    )

    return <>{countryData}</>
  }
}

CountryData.propTypes = {
  data: PropTypes.shape({
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
  }).isRequired,
  removeCountry: PropTypes.func.isRequired,
}
