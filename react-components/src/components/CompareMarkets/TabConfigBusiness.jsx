import React from 'react'
import Services from '@src/Services'

const rankOutOf = (rank, total) => {
  return (
    <>
      {rank} of {total}
    </>
  )
}

export default {
  tabName: 'DOING BUSINESS',
  sourceAttributions: [
    {
      title: 'Ease of Doing Business Rank',
      linkText: 'World Bank',
      linkTarget: 'https://www.doingbusiness.org/en/data/doing-business-score',
      text: 'CC BY 4.0.',
    },
    {
      title: 'Rule of Law ranking',
      linkText: 'The Global Innovation Index 2020.',
      linkTarget: 'https://www.globalinnovationindex.org/gii-2020-report',
    },
    {
      title: 'Corruption Perceptions Index',
      linkText: 'Transparency International',
      linkTarget: 'https://www.transparency.org/en/cpi/2019/results/table',
      text: 'CC BY-ND 4.0',
    },
  ],

  columns: {
    'eod-business': {
      name: 'Ease of doing business rank',
      className: 'text-align-right',
      render: (data) =>
        rankOutOf(
          data.EaseOfDoingBusiness[0].rank,
          data.EaseOfDoingBusiness[0].max_rank
        ),
      year: (data) => data.EaseOfDoingBusiness[0].year,
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Ease of Doing Business rank indicates how easy or hard it is to do business somewhere.</p>
          <p>The rank is from 1 (easy to do business) to 190 (hard to do business).</p>
          <p>This can help you decide whether to export somewhere and whether you need professional help to do so.</p>
         `,
      },
    },
    'rule-of-law': {
      name: 'Rule of Law ranking',
      className: 'text-align-right',
      render: (data) => rankOutOf(data.RuleOfLaw[0].rank, 131),
      year:(data) => data.RuleOfLaw[0].year,
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
    cpi: {
      name: 'Corruption Perceptions Index',
      className: 'text-align-right',
      render: (data) => {
        return rankOutOf(
          data.CorruptionPerceptionsIndex[0].rank,
          data.CorruptionPerceptionsIndex[0].total
        )
      },
      year: (data) => data.CorruptionPerceptionsIndex[0].year,
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Corruption Perceptions Index is published every year by Transparency International.</p>
          <p>The index ranks  public-sector corruption  according to experts and business people. Here we use a rank from 1 (clean) to 180 (highly corrupt).</p>
          <p>This gives you an idea of how easy or difficult it is to deal with local officials and businesses, and to get paid.</p>
         `,
      },
    },
  },
  dataFunction: (countries) =>
    Services.getCountryData(
      countries,
      JSON.stringify([
        { model: 'CorruptionPerceptionsIndex', filter: { year: '2020' } },
        { model: 'EaseOfDoingBusiness' },
        { model: 'RuleOfLaw' },
      ])
    ),
}
