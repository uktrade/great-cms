import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Tooltip } from '@components/tooltip/Tooltip'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import { formatLanguages } from '@src/components/TargetAgeGroupInsights/utils'

export const Table = memo(({ languages, infoMomenent, tooltip }) => {
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
                <Tooltip id="languages-in-target-market-tooltip" {...tooltip} />
              )}
            </Stats>
            <hr className="hr hr--light" />
            <Stats
              data={infoMomenent || notAvailable}
              descriptionClassName="body-l"
            >
              <div className="fas fa-lg fa-info-circle text-blue-deep-30" />
            </Stats>
          </div>
        </div>
      </div>
    </ToggleSnapshot>
  )
})

Table.propTypes = {
  languages: PropTypes.shape({
    date: PropTypes.string,
    language: PropTypes.arrayOf({
      name: PropTypes.string,
      note: PropTypes.string,
      percent: PropTypes.number,
    }),
  }),
  infoMomenent: PropTypes.string.isRequired,
  tooltip: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.string.isRequired,
  }),
}

Table.defaultProps = {
  tooltip: null,
  languages: [],
}
