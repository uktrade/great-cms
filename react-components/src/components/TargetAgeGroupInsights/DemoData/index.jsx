import React, { memo } from 'react'
import { Tooltip } from '@components/tooltip/Tooltip'

import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'

export const DemoData = memo(
  ({ population, cpi, internetPercentage, internetTotal, languages }) => {
    return (
      <>
        <h3 className="body-l-b m-b-xs">Global demographic data</h3>
        <div className="stat-group">
          <div className="grid">
            <div className="c-1-3">
              <Stats
                header="Total population"
                data={population ? `${population} million` : notAvailable}
              />
            </div>
            <div className="c-1-3">
              <Stats
                header="Access to the internet (total)"
                data={internetPercentage}
              />
            </div>
            <div className="c-1-3">
              <Stats header="Consumer Price Index" data={cpi || notAvailable}>
                <Tooltip
                  className="f-r"
                  id="corruption-perception-index-tooltip"
                  position="right"
                  heading="What is the Consumer Price Index?"
                  content="<p>The CPI measures the average change in prices over time that consumers pay for a basket of goods and services for their household, this is also known as inflation. It is used to estimate the change in total cost of this basket and the effect this has on the purchasing power of the country’s unit of currency.</p>"
                />
              </Stats>
            </div>
          </div>
        </div>
        <div className="stat-group radius-bottom-xs">
          <div className="grid">
            <div className="c-full">
              <Stats
                header="Languages in your target market"
                data={languages || notAvailable}
              />
            </div>
          </div>
        </div>
      </>
    )
  }
)

DemoData.propTypes = {
  population: PropTypes.string.isRequired,
  cpi: PropTypes.string.isRequired,
  internetPercentage: PropTypes.number.isRequired,
  internetTotal: PropTypes.number.isRequired,
  languages: PropTypes.string.isRequired,
}
