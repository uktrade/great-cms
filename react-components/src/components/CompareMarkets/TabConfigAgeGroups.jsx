import React from 'react'
import Services from '@src/Services'
import actions from '@src/actions'
import { millify, normaliseValues } from '../../Helpers'
import Filter from './Filter'

let localActiveFilter = {}

const filterMapping = {
  sector0_14: { label: '0-14', groups: ['0-4', '5-9', '10-14'] },
  sector15_19: { label: '15-19', groups: ['15-19'] },
  sector20_24: { label: '20-24', groups: ['20-24'] },
  sector25_34: { label: '25-34', groups: ['25-29', '30-34'] },
  sector35_44: { label: '35-44', groups: ['35-39', '40-44'] },
  sector45_54: { label: '45-54', groups: ['45-49', '50-54'] },
  sector55_64: { label: '55-64', groups: ['55-59', '60-64'] },
  sector65: {
    label: '65 and over',
    groups: [
      '65-69',
      '70-74',
      '75-79',
      '80-84',
      '85-89',
      '90-94',
      '95-99',
      '100+',
    ],
  },
}

const valueAndPercentage = (dataSet, gender) => {
  const value = dataSetByGender(dataSet, gender)
  const total = dataSetByGender(dataSet, null, null)
  return (
    <>
      <div className="body-l primary">
        {millify(value)}
      </div>
      <div className="body-m secondary text-black-60">
        {normaliseValues(value*100/total)}%
      </div>
    </>
    )
}


const populationFiltered = (dataSet, filter) => {
  const value = Object.keys(filterMapping).reduce((total, filterGroupKey) => {
    if (
      !filter || !Object.keys(filter).length ||
      filter[filterGroupKey]
    ) {
      return filterMapping[filterGroupKey].groups.reduce(
        (groupTotal, sourceKey) => groupTotal + (dataSet[sourceKey] || 0),
        total
      )
    }
    return total
  }, 0)
  return value * 1000 // Because the source data are in 1000s
}

const dataSetByGender = (dataSet, gender, filter=localActiveFilter) => {
  return dataSet
      .filter((row) => !gender || row.gender === gender)
      .reduce((total, row) => total + populationFiltered(row, filter), 0)
}

const yearByGender = (dataSet, gender) => {
  return (dataSet.filter((row) => !gender || row.gender === gender)[0] || {}).year
}

const setActiveFilter = (activeFilter) => {
  localActiveFilter = activeFilter
  Services.store.dispatch(actions.setLoaded())
}
const filter = (
  <>
    <div className="body-l-b">Select your target age groups</div>
    <Filter setActiveFilter={setActiveFilter} filters={filterMapping} />
  </>
)

export default {
  tabName: 'TARGET AGE GROUPS',
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
    },
    female_population: {
      name: 'Females in target group',
      className: 'text-align-right',
      render: (data) => valueAndPercentage(data.PopulationData, 'female'),
      year: (data) => yearByGender(data.PopulationData, 'female'),
    },
    male_population: {
      name: 'Males in target group',
      className: 'text-align-right',
      render: (data) => valueAndPercentage(data.PopulationData, 'male'),
      year: (data) => yearByGender(data.PopulationData, 'male'),
    },
  },

  dataFunction: (countries) => {
    return Services.getCountryData(countries, JSON.stringify([{model:'PopulationData',filter:{year:2020}}]))
  },
}
