import React, { useState, useEffect } from 'react'
import Services from '@src/Services'
import { normaliseValues } from '../../Helpers'

const MAX_ENTRIES = 5

export default function SocietyData(props) {
  const [societyData, setSocietyData] = useState([])

  const getCountryData = (country) => {
    if (societyData && societyData.length) {
      const country_data = Object.values(societyData).find(
        (x) => x[1].country === country
      )
      return country_data ? country_data[1] : []
    }
  }

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map((country) => {
        return country.country_name
      })
      Services.getSocietyByCountryData(countries)
        .then((result) => {
          setSocietyData(Object.entries(result))
        })
        .finally(() => {})
    }
  }, [props])

  const formatReligion = (religion) => {
    return religion.name + (religion.percent ? ' ' + religion.percent + '%' : '')
  }

  const formatLanguage = (language) => {
    let isOfficial = language.note == 'official'
    return language.name + (isOfficial ? ' (official)' : '')
  }

  const getEntries = (list, func) => {
    const entries = Object.values(list).slice(0, MAX_ENTRIES).map((entry, key) => {
      return <p className="entry body-m" key={key}>{func(entry)}</p>
    })
    return entries
  }

  const comparisonMarkets = props.comparisonMarkets

  const sourceAttribution = (
    <p className="source-attribution body-s">
      <strong className="body-s-b">
        Religion
      </strong>
      :&nbsp;
      <a
        href="https://www.cia.gov/the-world-factbook"
        target="_blank"
      >
        Central Intelligence Agency
      </a>
      &nbsp;
      <strong className="body-s-b">
        Languages
      </strong>
      :&nbsp;
      <a
        href="https://www.cia.gov/the-world-factbook"
        target="_blank"
      >
        Central Intelligence Agency
      </a>
      &nbsp;
      <strong className="body-s-b">
        Rule of law
      </strong>
      :&nbsp;
      <a
        href="https://www.globalinnovationindex.org/gii-2020-report"
        target="_blank"
      >
        The Global Innovation Index 2020
      </a>
    </p>
  )
  
  let DATA_NA = 'Data not available'
  let dataTable

  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
    const tableBody = Object.values(comparisonMarkets).map((market) => {
      let data = getCountryData(market.country_name)
      let dataRow
      if (data) {
        dataRow = (
          <React.Fragment>
            <td className="religion align-left align-top">
            {data.religions
                ? getEntries(data.religions.religion, formatReligion)
                : DATA_NA
              }
            </td>
            <td className="language align-left align-top">
              {data.languages
                ? getEntries(data.languages.language, formatLanguage)
                : DATA_NA
              }
            </td>
            <td className="rule-of-law align-top">
              {data.rule_of_law
                ? normaliseValues(data.rule_of_law.score)
                : DATA_NA
              }
            </td>
          </React.Fragment>
        )
      } else {
        dataRow = (
          <td colSpan="7" className="no-data">
            No data currently available for this country
          </td>
        )
      }
      return (
        <tr
          key={`market-${market.country_name}`}
          id={`market-${market.country_name}`}
        >
          <td className="p-v-xs name">
            <div style={{ whiteSpace: 'nowrap' }}>
              <button
                type="button"
                onClick={props.removeMarket}
                className="button button--only-icon button--tertiary button--small m-r-xxs"
                data-id={market.country_iso2_code}
                aria-label={`Remove ${market.country_name}`}
              >
                <i className="fa fa-trash-alt icon--border" />
              </button>
              <span
                className={`market-${market.country_name}` + ' ' + 'body-l-b'}
              >
                {market.country_name}
              </span>
            </div>
          </td>
          {dataRow}
        </tr>
      )
    })
    dataTable = (
      <span>
        <table className="m-v-0 border-blue-deep-20">
          <thead>
            <tr>
              <th className="body-s-b"></th>
              <th className="align-left body-s-b">
                Religion
              </th>
              <th className="align-left body-s-b">
                Language
              </th>
              <th className="body-s-b">
                Rule of law score
              </th>
            </tr>
          </thead>
          <tbody>{tableBody}</tbody>
        </table>
        {sourceAttribution}
      </span>
    )
  }
  return <div>{dataTable}</div>
}
