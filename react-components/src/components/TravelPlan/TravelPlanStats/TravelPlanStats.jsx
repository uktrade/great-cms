import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Tooltip } from '@components/tooltip/Tooltip'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import { formatLanguages } from '@src/components/TargetAgeGroupInsights/utils'

export const TravelPlanStats = memo(({ languages, tooltip }) => {
  const formatedLanguages = formatLanguages(
    languages.cia_factbook_data.languages.language
  )

  return (
    <ToggleSnapshot isOpen={false}>
      <div className="width-full">
        <div className="grid">
          <div className="c-full">
            <Stats
              header="The main languages in your chosen market are:"
              data={formatedLanguages || notAvailable}
              childPosition="bottom"
            >
              {tooltip && (
                <Tooltip
                  id="languages-in-target-market-tooltip"
                  title={tooltip.title}
                  content={`<p>${tooltip.content}</p>`}
                  className="m-t-xs"
                />
              )}
            </Stats>
          </div>
        </div>
      </div>
    </ToggleSnapshot>
  )
})

TravelPlanStats.propTypes = {
  languages: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }).isRequired,
  tooltip: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.string.isRequired,
  }),
}
