import React from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '../EducationalMomentTooltip'

const notAvailable = 'Data not available'

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
  languages
}) {
  return (
    <div className="target-age-group-insights m-t-m">
      <div className="grid">
        <h3 className='body-l-b m-b-xs'>Global demographic data</h3>
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Total population</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{population ? `${population} million` : notAvailable }</dd>
            </dl>
          </div>
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Access to the internet (total)</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{internet_percentage ? `${internet_percentage}% (${internet_total} million)` : notAvailable }</dd>
            </dl>
          </div>
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Consumer Price Index</dt>
              <EducationalMomentTooltip
                id={`corruption-perception-index-tooltip`}
                heading="What is the Consumer Price Index?"
                description="The CPI measures the average change in prices over time that consumers pay for a basket of goods and services for their household, this is also known as inflation. It is used to estimate the change in total cost of this basket and the effect this has on the purchasing power of the country’s unit of currency."
              />
            <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{cpi || notAvailable }</dd>
            </dl>
          </div>
      </div>

      <div className="grid">
        <div className="c-full">
          <dl className="statistic">
            <dt className="statistic__caption">Languages in your target market</dt>
            <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{languages || notAvailable }</dd>
          </dl>
        </div>
      </div>
      <div className="grid">
        <h3 className='body-l-b m-b-xs'>Data specific for you target age group</h3>
          <div className="c-1-3">
            <dl className="statistic">
              <dt className="statistic__caption">Target age population</dt>
              <dd className="statistic__figure h-xs p-b-0 p-t-xxs">{target_population ? `${target_population} million` : notAvailable }</dd>
            </dl>
          </div>

        <div className="c-2-3">
          <div className='statistic'>
            <div className="statistic__group">
              <dl>
                <dt className="statistic__caption p-t-xs">Female in your target group</dt>
                <dd className="statistic__figure h-xs p-b-0 p-t-s">{female ? `${female} million`: '' }</dd>
              </dl>
              <dl>
                <dt className="statistic__caption p-t-xs">Male in your target group</dt>
                <dd className="statistic__figure h-xs p-b-0 p-t-s">{female ? `${male} million`: '' }</dd>
              </dl>
              { !!(female && female !== 0) &&
                <div className="statistic__percentage bg-red-80 radius m-b-xs">
                  <span className='bg-blue-deep-80 radius' style={{ width: `${(female/target_population)*100}%` }} />
                </div>
              }
            </div>
            {!female && <span className='h-xs p-t-0'>{notAvailable}</span>}
          </div>
          <div className='statistic'>
            <div className="statistic__group">
              <dl>
                <dt className="statistic__caption p-t-xs">Living in urban areas</dt>
                <dd className="statistic__figure h-xs p-b-0 p-t-s">{urban ? `${urban}%`: '' }</dd>
              </dl>
              <dl>
                <td className="statistic__caption p-t-xs">Living in rural areas</td>
                <dd className="statistic__figure h-xs p-b-0 p-t-s">{urban ? `${rural}%`: '' }</dd>
              </dl>
              { !!(urban && urban !== 0) &&
                <div className="statistic__percentage bg-red-80 radius m-b-xs">
                  <span className='bg-blue-deep-80 radius' style={{ width: `${urban}%` }} />
                </div>
              }
            </div>
            {!urban && <span className='h-xs p-t-0'>{notAvailable}</span>}
          </div>
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
