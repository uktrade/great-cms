import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { AgeGroupData } from './AgeGroupData'
import { DemoData } from './DemoData'

export const Table = memo(
  ({
    population,
    cpi,
    internetPercentage,
    internetTotal,
    languages,
    urban,
    rural,
    female,
    male,
    targetPopulation,
  }) => (
    <div className="m-t-m">
      <DemoData
        population={population}
        internetPercentage={internetPercentage}
        internetTotal={internetTotal}
        cpi={cpi}
        languages={languages}
      />
      <AgeGroupData
        targetPopulation={targetPopulation}
        female={female}
        male={male}
        urban={urban}
        rural={rural}
      />
    </div>
  )
)

Table.propTypes = {
  population: PropTypes.string.isRequired,
  cpi: PropTypes.string.isRequired,
  urban: PropTypes.number,
  rural: PropTypes.number,
  female: PropTypes.number,
  male: PropTypes.number,
  internetPercentage: PropTypes.number.isRequired,
  internetTotal: PropTypes.number.isRequired,
  targetPopulation: PropTypes.number,
  languages: PropTypes.string.isRequired,
}

Table.defaultProps = {
  urban: '',
  rural: '',
  female: '',
  male: '',
  targetPopulation: '',
}
