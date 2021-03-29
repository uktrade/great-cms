import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { AgeGroupData } from './AgeGroupData'
import { DemoData } from './DemoData'

export const Table = memo(
  ({
    totalPopulation,
    cpi,
    internetData,
    languages,
    urbanPopulationTotal,
    ruralPopulationTotal,
    femaleTargetAgePopulation,
    maleTargetAgePopulation,
    totalTargetAgePopulation,
  }) => (
    <div className="m-t-m">
      <DemoData
        population={totalPopulation}
        internetData={internetData}
        cpi={cpi}
        languages={languages}
      />
      <AgeGroupData
        targetPopulation={totalTargetAgePopulation}
        female={femaleTargetAgePopulation}
        male={maleTargetAgePopulation}
        urban={urbanPopulationTotal}
        rural={ruralPopulationTotal}
      />
    </div>
  )
)

Table.propTypes = {
  totalPopulation: PropTypes.number,
  totalTargetAgePopulation: PropTypes.number,
  cpi: PropTypes.number,
  internetData: PropTypes.number,
  urbanPopulationTotal: PropTypes.number,
  ruralPopulationTotal: PropTypes.number,
  femaleTargetAgePopulation: PropTypes.number,
  maleTargetAgePopulation: PropTypes.number,
  languages: PropTypes.string,
}

Table.defaultProps = {
  totalPopulation: '',
  totalTargetAgePopulation: '',
  cpi: '',
  internetData: '',
  urbanPopulationTotal: '',
  ruralPopulationTotal: '',
  femaleTargetAgePopulation: '',
  maleTargetAgePopulation: '',
  languages: '',
}
