import React from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '../EducationalMomentTooltip'

export default function Table({
  population,
  cpi,
  urban,
  rural,
  female,
  male,
  internet_percentage,
  internet_total,
  target_population,
  target_population_percentage,
  languages
}) {
  return (
    <div className="target-age-group-insights m-t-m">
      <div className="grid">
        <h3 className='body-l-b m-b-xs'>Global demographic data</h3>
        {population && (
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Total population</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{population} million</dd>
            </dl>
          </div>
        )}
        {internet_percentage && internet_total && (
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Access to the internet (total)</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{internet_percentage}% ({internet_total} million)</dd>
            </dl>
          </div>
        )}
        {cpi && (
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Consumer Price Index</dt>
              <EducationalMomentTooltip
                id={`corruption-perception-index-tooltip`}
                heading="What is the Consumer Price Index?"
                description="The CPI measures the average change in prices over time that consumers pay for a basket of goods and services for their household, this is also known as inflation. It is used to estimate the change in total cost of this basket and the effect this has on the purchasing power of the country’s unit of currency."
              />
            <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{cpi}</dd>
            </dl>
          </div>
        )}
      </div>

      {languages && (
        <div className="grid">
          <div className="c-full">
            <dl className="statistic">
              <dt className="statistic__caption">Languages in your target market</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{languages}</dd>
            </dl>
          </div>
        </div>
      )}
      <div className="grid">
        <h3 className='body-l-b m-b-xs'>Data specific for you target age group</h3>
        {target_population && target_population_percentage && (
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Target age population</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{target_population} million</dd>
            </dl>
          </div>
        )}

        <div className="c-2-3">
          {female && male && (
            <div className='statistic'>
              <div className="statistic__group">
                <dl>
                  <dt className="statistic__caption p-t-xs">Female in your target group</dt>
                  <dd className="statistic__figure h-xs p-b-0 p-t-s">{female} million</dd>
                </dl>
                <dl>
                  <dt className="statistic__caption p-t-xs">Male in your target group</dt>
                  <dd className="statistic__figure h-xs p-b-0 p-t-s">{male} million</dd>
                </dl>
              </div>
              <div className="statistic__percentage bg-red-80 radius m-b-xs">
                <span className='bg-blue-deep-80 radius' style={{ width: '51%' }} />
              </div>
            </div>
          )}
          {urban && rural && (
            <div className='statistic'>
              <div className="statistic__group">
                <dl>
                  <dt className="statistic__caption p-t-xs">Living in urban areas</dt>
                  <dd className="statistic__figure h-xs p-b-0 p-t-s">{urban}%</dd>
                </dl>
                <dl>
                  <td className="statistic__caption p-t-xs">Living in rural areas</td>
                  <dd className="statistic__figure h-xs p-b-0 p-t-s">{rural}%</dd>
                </dl>
              </div>
              <div className="statistic__percentage bg-red-80 radius m-b-xs">
                <span className='bg-blue-deep-80 radius' style={{ width: `${urban}%` }} />
              </div>
            </div>
          )}
        </div>
      </div>
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
