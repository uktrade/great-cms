/* eslint-disable import/prefer-default-export */
import React, { memo } from 'react'
import PropTypes from 'prop-types'

import EducationalMomentTooltip from '@src/components/EducationalMomentTooltip'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'

export const Table = memo(({ languages, infoMomenent, tooltip }) => {
  const { heading, description } = tooltip
  return (
    <ToggleSnapshot isOpen={false}>
      <div className="width-full">
        <div className="grid">
          <div className="c-full">
            <Stats header="The main languages in your chosen market are:" data={languages || notAvailable}>
              <EducationalMomentTooltip
                id="languages-in-target-market-tooltip"
                heading={heading}
                description={description}
              />
            </Stats>
            <hr className="hr hr--light" />
            <Stats data={infoMomenent || notAvailable} descriptionClassName="body-l">
              <div className="fas fa-lg fa-info-circle text-blue-deep-30" />
            </Stats>
          </div>
        </div>
      </div>
    </ToggleSnapshot>
  )
})

Table.defaultProps = {
  tooltip: {
    heading: 'Tooltip',
    description: 'Educational moment description',
  },
}

Table.propTypes = {
  languages: PropTypes.string.isRequired,
  infoMomenent: PropTypes.string.isRequired,
  tooltip: PropTypes.shape({
    heading: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
  }),
}
