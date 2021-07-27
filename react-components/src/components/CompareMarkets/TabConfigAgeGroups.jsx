import React from 'react'
import Services from '@src/Services'
import actions from '@src/actions'
import { millify, normaliseValues, listJoin } from '../../Helpers'
import Filter from './Filter'
import { dataSetByGender, filterMapping } from './AgeGroupFilter'

let localActiveFilter = {}

const valueAndPercentage = (dataSet, gender) => {
  const value = dataSetByGender(dataSet, localActiveFilter, gender)
  const total = dataSetByGender(dataSet, null, null)
  return (
    <>
      <div className="body-l primary">{millify(value)}</div>
      <div className="body-m secondary text-black-60">
        {normaliseValues((value * 100) / total, 0)}%
      </div>
    </>
  )
}

const yearByGender = (dataSet, gender) => {
  return (dataSet.filter((row) => !gender || row.gender === gender)[0] || {})
    .year
}

const setActiveFilter = (activeFilter) => {
  localActiveFilter = activeFilter
  Services.store.dispatch(actions.setLoaded())
}

const filter = (
  <div className="overflow-hidden">
    <div className="body-l-b">Select your target age groups</div>
    <Filter
      filterId="age-groups"
      setActiveFilter={setActiveFilter}
      filters={filterMapping}
    />
  </div>
)

const renderFilter = () => {
  const filterNames = Object.keys(localActiveFilter).map((mapFilter) => filterMapping[mapFilter].label)
  if(filterNames.length) {
    return `Demographics for age groups ${listJoin(filterNames)}`
  }
  return 'Demographics for all age groups'
}

export default {
  tabName: 'DEMOGRAPHICS',
  filter,
  sourceAttributions: [
    {
      title: 'Population data',
      linkText: 'United Nations',
      linkTarget: 'https://population.un.org/wup/Download/',
      text: 'CC BY 3.0 IGO.',
    },
  ],

  columns: {
    total_population: {
      name: 'Target age group population',
      className: 'text-align-right',
      render: (data) => valueAndPercentage(data.PopulationData, null),
      year: (data) => yearByGender(data.PopulationData, null),
      tooltip: {
        position: 'right',
        content: `
          <p>The population of your target age group in the selected countries and territories. This indicates how many potential customers you have.</p>
         `,
      },
    },
    female_population: {
      name: 'Females',
      className: 'text-align-right',
      render: (data) => valueAndPercentage(data.PopulationData, 'female'),
      year: (data) => yearByGender(data.PopulationData, 'female'),
      tooltip: {
        position: 'right',
        title: 'What is \'Female population percentage\'?',
        content: `
          <p>The percentage of your target age group that are female.</p>
         `,
      },
    },
    male_population: {
      name: 'Males',
      className: 'text-align-right',
      render: (data) => valueAndPercentage(data.PopulationData, 'male'),
      year: (data) => yearByGender(data.PopulationData, 'male'),
      tooltip: {
        position: 'right',
        title: 'What is \'Male population percentage\'?',
        content: `
          <p>The percentage of your target age group that are male.</p>
         `,
      },
    },
  },
  caption: () => <caption className="visually-hidden">{renderFilter()}</caption>,
  dataFunction: (countries) => {
    return Services.getCountryData(
      countries,
      JSON.stringify([{ model: 'PopulationData', filter: { year: 2020 } }])
    )
  },
}
