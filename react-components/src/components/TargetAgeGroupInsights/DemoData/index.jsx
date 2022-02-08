import React, { memo } from 'react'
import { Tooltip } from '@components/tooltip/Tooltip'

import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues, get } from '@src/Helpers'
import { formatLanguages } from '@src/components/TargetAgeGroupInsights/utils'

const formatNumber = (val) =>
  Number(val) ? millify(Number(val)) : notAvailable

export const DemoData = memo(({ totalPopulation, cpi, internetData, languages }) => {
  return (
    <>
      <h3 className="body-l-b m-b-xs m-t-s">Global demographic data</h3>
      <div className="stat-group m-b-s">
        <div className="grid">
          <div className="c-1-3">
            <Stats header="Total population" data={formatNumber(totalPopulation)} />
          </div>
          <div className="c-1-3">
            <Stats
              header="Access to the internet (total)"
              data={
                internetData
                  ? `${normaliseValues(
                      internetData
                    )}% <div class="body-m">(${millify(
                      internetData * totalPopulation * 10
                    )})</div>`
                  : notAvailable
              }
            />
          </div>
          <div className="c-1-3">
            <Stats
              header="Consumer Price Index"
              data={normaliseValues(cpi) || notAvailable}
            >
              <Tooltip
                className="f-r"
                id="corruption-perception-index-tooltip"
                position="right"
                title="What is the Consumer Price Index?"
                content="<p>The CPI measures the average change in prices over time that consumers pay for a basket of goods and services for their household, this is also known as inflation. It is used to estimate the change in total cost of this basket and the effect this has on the purchasing power of the country’s unit of currency.</p>"
              />
            </Stats>
          </div>

          <div className="c-full">
            <Stats
              header="Languages in your target market"
              data={
                languages
                  ? formatLanguages(get(languages, 'language', []))
                  : notAvailable
              }
            />
          </div>
        </div>
      </div>
    </>
  )
})

DemoData.propTypes = {
  totalPopulation: PropTypes.number,
  cpi: PropTypes.string,
  internetData: PropTypes.string,
  languages: PropTypes.shape({
    language: PropTypes.arrayOf(PropTypes.object)
  }),
}
DemoData.defaultProps = {
  totalPopulation: null,
  cpi: '',
  internetData: '',
  languages: null,
}
