export const filterMapping = {
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

const populationFiltered = (dataSet, filter) => {
  const value = Object.keys(filterMapping).reduce((total, filterGroupKey) => {
    if (!filter || !Object.keys(filter).length || filter[filterGroupKey]) {
      return filterMapping[filterGroupKey].groups.reduce(
        (groupTotal, sourceKey) => groupTotal + (dataSet[sourceKey] || 0),
        total
      )
    }
    return total
  }, 0)
  return value * 1000 // Because the source data are in 1000s
}

export const dataSetByGender = (dataSet, filter, gender) => {
  return dataSet
    .filter((row) => !gender || row.gender === gender)
    .reduce((total, row) => total + populationFiltered(row, filter), 0)
}
