import React from 'react'
import PropTypes from 'prop-types'
import { slugify } from '../Helpers'


export default class CountryData extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      //has to come from data TODO
      time: new Date().toLocaleTimeString('en-GB', {timeZone: 'Australia/Lord_Howe'})
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
    const easeofdoingbusiness = this.props.data.easeofdoingbusiness
    const corruption_perceptions_index = this.props.data.corruption_perceptions_index
    const lastyear_import_data = this.props.data.last_year_data
    const export_duty = this.props.data.export_duty
    const sectionID = `export-market-data-${slugify(this.props.data.country)}`

    const utz_offset = '+1030' //Fix me
    const timezone = 'Australia/Lord_Howe' //Fix me
    const rules_regulations = {commodity_name: 'Gin'} //this.props.data.rules_regulations

    const countryData = (
      <>
      <section id={sectionID}>
          <h2 className="h-l p-b-0 inline-block">{ this.props.data.country }  </h2>
          <button
            onClick={this.handleClick}
            id="remove-country"
            className="remove-country-button">
            Remove
            <span className="visually-hidden">{ this.props.data.country }</span>
          </button>
          <div className="flex-grid">
              <div className="c-1-3" id="export-market-data-ease-of-doing-business-rank">
                  <figure className="statistic">
                      <figcaption>
                          <p className="statistic__caption">Ease of doing business rank</p>
                      </figcaption>
                      <p className="statistic__figure">
                          {
                            (easeofdoingbusiness.year_2019) ? (
                              <>
                                <span>{easeofdoingbusiness.year_2019}</span>
                                <span className="statistic__details">out of { easeofdoingbusiness.total }</span>
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
                          (corruption_perceptions_index.rank) ? (
                            <>
                              { corruption_perceptions_index.rank }
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
                          <span className="statistic__details">GMT { utz_offset } { timezone }</span>
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
                          (export_duty > 0) ? (
                            <>
                              { export_duty }%
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
                          { lastyear_import_data.trade_value } USD
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
