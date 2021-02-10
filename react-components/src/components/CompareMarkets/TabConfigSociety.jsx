import React from 'react'
import Services from '@src/Services'
import {
  normaliseValues,
  get,
  capitalize,
  stripPercentage,
} from '../../Helpers'

const rankOutOf = (data, key) => {
  return (
    data &&
    data[key] && (
      <>
        {data[key]} of {data.total}
      </>
    )
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

const ruleOfLawRanking = (data) => {
  // TODO: get these 'total' and 'year' values from API
  const rankingTotal = 131
  const year = 2020
  const decorated = { ...data, total: rankingTotal, year }
  return data && (
    <>
      {rankOutOf(decorated, 'rank')}
      {decorated.year && (
        <div className="body-m text-black-60 display-year">
          {decorated.year}
        </div>
      )}
    </>
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
    religion: {
      name: 'Religion',
      className: 'align-top',
      render: (data) => religion(get(data, 'religions')),
    },
    language: {
      name: 'Language',
      className: 'align-top',
      render: (data) => language(get(data, 'languages')),
    },
    'rule-of-law': {
      name: 'Rule of Law ranking',
      className: 'align-top',
      render: (data) => ruleOfLawRanking(get(data, 'rule_of_law')),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The strength of the law varies from place to place.</p>
          <p>The rank is from low (law abiding) to high (not law abiding), using factors like contract enforcement, property rights, police, and the courts.</p>
          <p>This indicates how hard it may be to follow regulations and take legal action if something goes wrong.</p>
         `,
      },
    },
  },
  dataFunction: Services.getSocietyByCountryData,
}
