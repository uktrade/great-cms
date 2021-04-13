import React, { memo, useState, cloneElement, useEffect } from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { camelizeObject } from '@src/Helpers'

export const ToggleDataTable = ({ countryIso2Code, groups, selectedGroups: selected, children, url }) => {
    const [isOpen, setIsOPen] = useState(false)
    const [selectedGroups, setSelectedGroups] = useState(selected)
    const [data, setData] = useState({})
    const targetGroupLabels = groups
      .filter((group) => selectedGroups.includes(group.key))
      .map((group) => group.label)
    const showTable = Object.keys(data).length >= 1 && !isOpen
    const getCountryData = () => {
      Services.getCountryAgeGroupData({
        country_iso2_code: countryIso2Code,
        target_age_groups: selectedGroups,
        section_name: url,
      })
        .then((result) => {
          setData(camelizeObject(camelizeObject(result).populationData))
        })
        .catch((error) => console.log(error))
    }
    useEffect(() => {
      if (selectedGroups.length > 0) {
        getCountryData()
      }
    }, [countryIso2Code])

    const submitForm = (event) => {
      event.preventDefault()
      setIsOPen(!isOpen)
      getCountryData()
    }

    const handleChange = (event) => {
      const { value } = event.target
      const isAlreadySelected = selectedGroups.find((group) => group === value)
      const updatedSelectedGroups = isAlreadySelected
        ? selectedGroups.filter((group) => group !== value)
        : [...selectedGroups, value]

      setSelectedGroups(updatedSelectedGroups)
    }
    return (
      <>
        <h3 className="body-l-b">Select target age groups</h3>
        <div className="selected-groups">
          <div className="selected-groups__button">
            <button
              className="button button--tiny-toggle"
              type="button"
              onClick={() => setIsOPen(!isOpen)}
            >
              <i className={`fa fa-chevron-circle-${isOpen ? 'up' : 'down'}`} />
            </button>
          </div>
          <ul className="selected-groups__items">
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
          <form onSubmit={submitForm}>
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

            <button className="button button--secondary m-t-s" type="submit">
              Confirm
            </button>
          </form>
        )}
        {showTable && cloneElement(children, { ...data })}
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
  children: PropTypes.element.isRequired,
  selectedGroups: PropTypes.arrayOf(PropTypes.string.isRequired),
  url: PropTypes.string.isRequired,
}

ToggleDataTable.defaultProps = {
  groups: [],
  selectedGroups: [],
}
