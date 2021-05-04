import React from 'react'
import Services from '@src/Services'
import {
  normaliseValues,
  get,
  capitalize,
  stripPercentage,
} from '../../Helpers'

const formatUrbanRural = (data) => {
  const out = data.reduce(
    (running, row) => {
      const rowVal = { ...running }
      rowVal[row.urban_rural] = row.value
      rowVal.total += row.value
      return rowVal
    },
    { total: 0 }
  )
  return (
    <>
      <div className="urban">
        Urban - {normaliseValues((out.urban * 100) / out.total, 0)}%
      </div>
      <div className="rural">
        Rural - {normaliseValues((out.rural * 100) / out.total, 0)}%
      </div>
    </>
  )
}

const formatEntry = (data) => {
  const name = stripPercentage(data.name)
  const percent = data.percent ? normaliseValues(data.percent, 0) : ''

  return percent ? `${name} - ${percent}%` : name
}

const getEntries = (list = {}) => {
  const maxEntries = 5
  const entries = Object.keys(list || {})
    .filter((key) => list[key].name)
    .slice(0, maxEntries)
    .map((key) => {
      return (
        <div className="entry body-l" key={key}>
          {formatEntry(list[key])}
        </div>
      )
    })
  return entries
}

const language = (data) => {
  const entries = getEntries(data.language)
  const { date, note } = data

  return (
    entries && (
      <>
        {entries}
        <div className="body-m text-black-60 display-note">
          {date}
          {date && note && '. '}
          {note && capitalize(note)}
        </div>
      </>
    )
  )
}

const religion = (data) => {
  const entries = getEntries(data.religion)
  const year = data.date
  return (
    entries && (
      <>
        {entries}
        {year && (
          <div className="body-m text-black-60 display-year">{year}</div>
        )}
      </>
    )
  )
}

export default {
  sourceAttributions: [
    {
      title: 'Religion',
      linkText: 'Central Intelligence Agency.',
      linkTarget: 'https://www.cia.gov/the-world-factbook',
    },
    {
      title: 'Languages',
      linkText: 'Central Intelligence Agency.',
      linkTarget: 'https://www.cia.gov/the-world-factbook',
    },
    {
      title: 'Rule of law',
      linkText: 'The Global Innovation Index 2020.',
      linkTarget: 'https://www.globalinnovationindex.org/gii-2020-report',
    },
  ],

  columns: {
    language: {
      name: 'Language',
      className: 'align-top',
      render: (data) => language(get(data, 'languages')),
    },
    religion: {
      name: 'Religion',
      className: 'align-top',
      render: (data) => religion(get(data, 'religions')),
    },
    urban_population: {
      name: 'Urban and Rural population',
      className: 'align-top',
      group: 'population',
      render: (data) => formatUrbanRural(data.PopulationUrbanRural),
      year: (data) => data.PopulationUrbanRural[0].year,
    },
  },
  headingClass: 'vertical-align-top',
  dataFunction: Services.getSocietyByCountryData,
  groups: {
    population: {
      dataFunction: (countries) =>
        Services.getCountryData(
          countries,
          JSON.stringify([
            { model: 'PopulationUrbanRural', filter: { year: 2020 } },
          ])
        ),
    },
  },
}
