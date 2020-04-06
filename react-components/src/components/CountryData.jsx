import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../Helpers'


export default class CountryData extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      time: new Date().toLocaleTimeString('en-GB', {timeZone: this.props.data.export_marketdata.timezone})
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
    this.setState({
      time: new Date().toLocaleTimeString('en-GB', {timeZone: this.props.data.export_marketdata.timezone})
    })
  }

  handleClick() {
    this.props.removeCountry(this.props.data)
  }

  render() {

    const export_marketdata = this.props.data.export_marketdata
    const utz_offset = this.props.data.utz_offset
    const rules_regulations = this.props.data.rules_regulations
    const lastyear_import_data = this.props.data.lastyear_import_data.last_year_data
    const lastyear_trade_value = this.props.data.lastyear_trade_value

    const sectionID = `export-market-data-${slugify(this.props.data.name)}`

    const countryData = (
      <>
      <section id={sectionID}>
          <h2 className="h-l p-b-0 inline-block">{ this.props.data.name }  </h2>
          <button
            onClick={this.handleClick}
            id="remove-country"
            className="remove-country-button">
            Remove
            <span className="visually-hidden">{ this.props.data.name }</span>
          </button>
          <div className="flex-grid">
              <div className="c-1-3" id="export-market-data-ease-of-doing-business-rank">
                  <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">Ease of doing business rank</p>
                      </figcaption>
                      <p className="statistic__figure">
                          {
                            (export_marketdata.easeofdoingbusiness.year_2019) ? (
                              <>
                                <span>{export_marketdata.easeofdoingbusiness.year_2019}</span>
                                <span className="statistic__details">out of { export_marketdata.easeofdoingbusiness.total }</span>
                              </>
                            ) : ( 'No data' )
                          }
                      </p>
                  </figure>
              </div>
              <div className="c-1-3" id="export-market-data-corruption-perception-index">
                  <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">Corruption Perception Index</p>
                      </figcaption>
                      <p className="statistic__figure">{
                          (export_marketdata.corruption_perceptions_index.rank) ? (
                            <>
                              { export_marketdata.corruption_perceptions_index.rank }
                            </>
                          ) : ( 'No data' ) }</p>
                  </figure>
              </div>
              <div className="c-1-3" id="export-market-data-local-time">
                  <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">Local time</p>
                      </figcaption>
                      <p className="statistic__figure">
                          <time>{ this.state.time }</time>
                          <span className="statistic__details">GMT { utz_offset } { export_marketdata.timezone }</span>
                      </p>
                  </figure>
              </div>
          </div>
          <div className="flex-grid">
              <div className="c-1-3" id="export-market-data-duty">
                  <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">Duty</p>
                      </figcaption>
                      <p className="statistic__figure">
                        {
                          (rules_regulations.export_duty > 0) ? (
                            <>
                              { rules_regulations.export_duty }%
                            </>
                          ) : ( 'No duty' )
                        }
                      </p>
                  </figure>
              </div>
              <div className="c-1-3" id="export-market-data-import-value">
                {
                  (lastyear_import_data) ? (
                    <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">
                              <span className="text-flag-red">{ rules_regulations.commodity_name }</span> import value in { lastyear_import_data.year }
                          </p>
                      </figcaption>
                      <p className="statistic__figure">
                          { lastyear_trade_value } USD
                          <span className="statistic__details">Source: Comtrade</span>
                      </p>
                  </figure>
                ) : null
              }
              </div>
              <div className="c-1-3" id="export-market-data-year-to-year-change">
                {
                  (lastyear_import_data) ? (
                    <figure className="statistic">
                        <figcaption>
                            <p className="statistic__caption">Year-to-year change</p>
                        </figcaption>
                        <p className="statistic__figure">
                            +{ lastyear_import_data.year_on_year_change }%
                        </p>
                    </figure>
                  ) : null
                }
              </div>
          </div>
      </section>
      <hr/>
      </>
    )

    return (
      <>
        {countryData}
      </>
    )
  }

}

CountryData.propTypes = {
  data: PropTypes.object.isRequired,
}

CountryData.defaultProps = {
  data: {}
}
