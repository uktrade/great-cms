import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../Helpers'

export default class CountryData extends React.Component {
  constructor(props) {
    super(props)
    const { data:{timezone} } = this.props
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
    const { data:{timezone} } = this.props
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
        export_duty: exportDuty,
        country,
        last_year_data: lastYearData,
        corruption_perceptions_index: corruptionPerceptionsIndex,
        easeofdoingbusiness,
      },
    } = this.props

    const { time } = this.state
    const sectionID = `export-market-data--${slugify(country)}`
    const commodityName = 'Gin' // this.props.data.rules_regulations

    const countryData = (
      <>
        <section id={sectionID} className="export-market-data">
          <h2 className="h-l p-b-0 inline-block">{country}</h2>
          <button type="button" onClick={this.handleClick} className="remove-country-button">
            Remove <span className="visually-hidden">{country}</span>
          </button>
          <div className="flex-grid">
            <div className="c-1-3 export-market-data__ease-of-doing-business-rank">
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Ease of doing business rank</p>
                </figcaption>
                <p className="statistic__figure">
                  {easeofdoingbusiness.year_2019 ? (
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
            <div className="c-1-3 export-market-data__corruption-perception-index">
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Corruption Perception Index</p>
                </figcaption>
                <p className="statistic__figure">
                  {corruptionPerceptionsIndex.rank ? <>{corruptionPerceptionsIndex.rank}</> : 'No data'}
                </p>
              </figure>
            </div>
            <div className="c-1-3 export-market-data__local-time">
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
            <div className="c-1-3 export-market-data__duty">
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Duty</p>
                </figcaption>
                <p className="statistic__figure">{exportDuty > 0 ? `${exportDuty}%` : 'No duty'}</p>
              </figure>
            </div>
            <div className="c-1-3 export-market-data__import-value">
              {lastYearData ? (
                <figure className="statistic">
                  <figcaption>
                    <p className="statistic__caption">
                      <span className="text-flag-red">{commodityName}</span> import value in {lastYearData.year}
                    </p>
                  </figcaption>
                  <p className="statistic__figure">
                    {lastYearData.trade_value} USD <span className="statistic__details">Source: Comtrade</span>
                  </p>
                </figure>
              ) : null}
            </div>
            <div className="c-1-3 export-market-data__year-to-year-change">
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

        <button type="button" className="button--ghost">
          Show more stats
        </button>
        <hr />
      </>
    )

    return <>{countryData}</>
  }
}

CountryData.propTypes = {
  data: PropTypes.shape({
    export_duty: PropTypes.number.isRequired,
    country: PropTypes.string.isRequired,
    utz_offset: PropTypes.string.isRequired,
    timezone: PropTypes.string.isRequired,
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
  }).isRequired,
  removeCountry: PropTypes.func.isRequired,
}
