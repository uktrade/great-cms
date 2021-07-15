import React, { useState, cloneElement, useEffect } from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { isArray, get } from '@src/Helpers'
import {
  dataSetByGender,
} from '@src/components/CompareMarkets/AgeGroupFilter'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const ToggleDataTable = ({
  countryIso2Code,
  groups,
  selectedGroups: selected,
  beforeTable,
  afterTable,
  url,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedGroups, setSelectedGroups] = useState(selected)
  const [data, setData] = useState({})
  const [rawData, setRawData] = useState({})
  const targetGroupLabels = groups
    .filter((group) => selectedGroups.includes(group.key))
    .map((group) => group.label)
  const showTable = Object.keys(data).length >= 1
  const saveAgeGroups = useDebounce(Services.getCountryAgeGroupData)

  useEffect(() => {
    Services.getCountryData(
      [{ country_iso2_code: countryIso2Code }],
      JSON.stringify([
        { model: 'PopulationData', filter: { year: 2020 } },
        { model: 'PopulationUrbanRural', filter: { year: 2021 } },
        { model: 'ConsumerPriceIndex', latest_only: true },
        { model: 'InternetUsage', latest_only: true },
        { model: 'CIAFactbook', latest_only: true },
      ])
    ).then((result) => {
      setRawData(result[countryIso2Code])
    })
  }, [countryIso2Code])

  useEffect(() => {
    if (rawData && Object.keys(rawData).length) {
      const activeGroups = selectedGroups.reduce((x, value) => {
        const l = x
        l[`sector${value.replace('-', '_').replace('+', '')}`] = true
        return l
      }, {})
      const urbanRural = rawData.PopulationUrbanRural && rawData.PopulationUrbanRural.reduce((x, row) => {
        const l = x
        l[row.urban_rural] = row.value
        return l
      }, {})
      const targetPopulation = ['male', 'female', null].reduce((x, key) => {
        const l = x
        l[`target${key || ''}`] = dataSetByGender(
          rawData.PopulationData,
          activeGroups,
          key
        )
        return l
      }, {})
      setData({
        internetData: get(rawData, 'InternetUsage.0.value'),
        languages: get(rawData, 'CIAFactbook.0.languages'),
        totalPopulation: dataSetByGender(rawData.PopulationData || [], null, null),
        cpi: get(rawData, 'ConsumerPriceIndex.0.value'),
        ...targetPopulation,
        ...urbanRural,
      })
    }
  }, [selectedGroups, rawData])

  const renderElements = (elements) => {
    if (!showTable || !elements) return ''
    const arrElements = isArray(elements) ? elements : [elements]
    return arrElements.map((child, index) => cloneElement(child, {key: index, ...data }))
  }

  const handleChange = (event) => {
    const { value } = event.target
    const isAlreadySelected = selectedGroups.find((group) => group === value)
    const updatedSelectedGroups = isAlreadySelected
      ? selectedGroups.filter((group) => group !== value)
      : [...selectedGroups, value]
    saveAgeGroups({
      section_name: url,
      target_age_groups: updatedSelectedGroups,
    })
    setSelectedGroups(updatedSelectedGroups)
  }
  return (
    <>
      {renderElements(beforeTable)}
      <h3 className="body-l-b">Target age groups</h3>
      <div className="selected-groups">
        <div className="selected-groups__button">
          <button
            className="button button--tiny-toggle"
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            aria-expanded={isOpen}
            aria-controls="target-age-groups"
          >
            <i className={`fa fa-chevron-circle-${isOpen ? 'up' : 'down'}`} />
            <span className="visually-hidden">{`${
              isOpen ? 'Close' : 'Open'
            } target age groups`}</span>
          </button>
        </div>
        <ul id="target-age-groups" className="selected-groups__items">
          {!isOpen &&
            selectedGroups.map((item) => (
              <li key={item} className="selected-groups__item">
                {item} years old
              </li>
            ))}
        </ul>
      </div>
      {targetGroupLabels.map((i) => (
        <span className="statistic-label body-m-b bg-blue-deep-20" key={i}>
          {i}
        </span>
      ))}
      {isOpen && (
        <ul className="form-group m-b-0">
          {groups.map(({ value, label }) => (
            <li className="great-checkbox width-full m-b-xs" key={value}>
              <input
                id={value}
                value={value}
                type="checkbox"
                onChange={handleChange}
                checked={selectedGroups.includes(value)}
              />
              <label htmlFor={value}>{label}</label>
            </li>
          ))}
        </ul>
      )}
      {renderElements(afterTable)}
    </>
  )
}

ToggleDataTable.propTypes = {
  countryIso2Code: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  beforeTable: PropTypes.arrayOf(PropTypes.element),
  afterTable: PropTypes.arrayOf(PropTypes.element),
  selectedGroups: PropTypes.arrayOf(PropTypes.string.isRequired),
  url: PropTypes.string.isRequired,
}

ToggleDataTable.defaultProps = {
  groups: [],
  selectedGroups: [],
  beforeTable: null,
  afterTable: null,
}
