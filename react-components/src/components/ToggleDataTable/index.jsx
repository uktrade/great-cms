import React, { memo, useState, cloneElement, useEffect } from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { mapData } from '@src/components/ToggleDataTable/utils'

export const ToggleDataTable = memo(
  ({ country, groups, selectedGroups: selected, children, url }) => {
    const [isOpen, setIsOPen] = useState(false)
    const [selectedGroups, setSelectedGroups] = useState(selected)
    const [data, setData] = useState({})
    const targetGroupLabels = groups
      .filter((group) => selectedGroups.includes(group.key))
      .map((group) => group.label)
    const showTable = Object.keys(data).length >= 1 && !isOpen

    const getCountryData = () => {
      Services.getCountryAgeGroupData({
        country,
        target_age_groups: selectedGroups,
        section_name: url,
      })
        .then(({ population_data }) => {
          setData(mapData(population_data))
        })
        .catch((error) => console.log(error))
    }

    useEffect(() => {
      if (selectedGroups.length > 0) {
        getCountryData()
      }
    }, [])

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
        <button
          className="button button--secondary button--icon m-t-xs m-r-xs"
          type="button"
          onClick={() => setIsOPen(!isOpen)}
        >
          <i className={`fa fa-chevron-circle-${isOpen ? 'up' : 'down'}`} />
          <span>{isOpen ? 'close' : 'open'}</span>
        </button>
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
)

ToggleDataTable.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  children: PropTypes.element.isRequired,
  selectedGroups: PropTypes.arrayOf(PropTypes.string.isRequired),
}

ToggleDataTable.defaultProps = {
  groups: [],
  selectedGroups: [],
}
