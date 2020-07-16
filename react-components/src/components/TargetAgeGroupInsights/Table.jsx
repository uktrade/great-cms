import React from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '../EducationalMomentTooltip'

export default function Table({ population, cpi, urban, rural, female, male, internet, targetPopulation }) {
  return (
    <div className="target-age-group-insights m-t-m">
      <div className="grid">
        {population && (
          <div className="c-1-4">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Total population</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{population} million</span>
              </p>
            </figure>
          </div>
        )}
        {internet && (
          <div className="c-1-4">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Access to internet</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{internet}% (312.32 million)</span>
              </p>
            </figure>
          </div>
        )}
        {cpi && (
          <div className="c-1-4">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Consumer Price Index</p>
                <EducationalMomentTooltip id={`cpi-tooltip`} heading="What is CPI?" description="Explanation of CPI" />
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{cpi}</span>
              </p>
            </figure>
          </div>
        )}
        {targetPopulation && (
          <div className="c-1-4">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Target age population</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{targetPopulation} million (100%)</span>
              </p>
            </figure>
          </div>
        )}
      </div>

      <div className="grid">
        {urban && rural && (
          <div className="c-1-2">
            <div className="statistic__percentage m-b-xs">
              <span style={{ width: `${urban}%` }}></span>
            </div>
            <div className="statistic__group">
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Living in urban areas</p>
                </figcaption>
                <p className="statistic__figure">
                  <span className="statistic__details">{urban}%</span>
                </p>
              </figure>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Living in rural areas</p>
                </figcaption>
                <p className="statistic__figure">
                  <span className="statistic__details">{rural}%</span>
                </p>
              </figure>
            </div>
          </div>
        )}
        {female && male && (
          <div className="c-1-2">
            <div className="statistic__percentage m-b-xs">
              <span style={{ width: '51%' }}></span>
            </div>
            <div className="statistic__group">
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Female in target group</p>
                </figcaption>
                <p className="statistic__figure">
                  <span className="statistic__details">{female} m</span>
                </p>
              </figure>
              <figure className="statistic">
                <figcaption>
                  <p className="statistic__caption">Male in target group</p>
                </figcaption>
                <p className="statistic__figure">
                  <span className="statistic__details">{male} m</span>
                </p>
              </figure>
            </div>
          </div>
        )}
      </div>

      <div className="grid">
        <div className="c-1-2">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Language</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">Dutch (official); Frisian, Low Saxon,</span>
            </p>
          </figure>
        </div>
      </div>

      <hr className="m-t-0 m-b-0" />
      <p className="target-age-group-insights__source">
        Source
        <br />
        CIA factbook
      </p>
    </div>
  )
}

Table.propTypes = {
  population: PropTypes.number,
  cpi: PropTypes.number,
  urban: PropTypes.number,
  rural: PropTypes.number,
  female: PropTypes.number,
  male: PropTypes.number,
  internet: PropTypes.number,
  targetPopulation: PropTypes.number
}
