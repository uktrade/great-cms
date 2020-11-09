import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import { mapData } from '@src/components/TargetAgeGroupInsights/utils'
import { Table } from './Table'
import { ProductData } from './ProductData'

export const DataSnapShot = memo(({
  country,
  groups
}) => {

  const [isOpen, setIsOPen] = useState(false)
  const [selectedGroups, setSelectedGroups] = useState([])
  const [data, setData] = useState({})
  const targetGroupLabels = groups
    .filter((group) => selectedGroups.includes(group.key))
    .map((group) => group.label)

  const showTable = Object.keys(data).length >= 1 && !isOpen

  const submitForm = (event) => {
    event.preventDefault()
    setIsOPen(!isOpen)

    Services.getMarketingCountryData({ country, target_age_groups: selectedGroups })
      .then((d) =>
        setData(mapData(d))
      )
      .catch((error) => console.log(error))
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
    <div className="target-age-group-insights">
      <ProductData />
      <h3 className="body-l-b">Select target age groups</h3>
      <button className="button button--secondary button--icon m-t-xs m-r-xs" type='button' onClick={() => setIsOPen(!isOpen)}>
        <i className="fa fa-chevron-circle-down" />
        <span>Open</span>
      </button>
      {targetGroupLabels.map(i => <span className='target-age-group-tag body-m-b bg-blue-deep-20' key={i}>{i}</span>)}

      {isOpen && (
        <form onSubmit={submitForm}>
          <ul className="form-group m-b-0">
            {groups.map(({ key, label }) => (
              <li className="great-checkbox width-full m-b-xs" key={key}>
                <input
                  id={key}
                  value={key}
                  type="checkbox"
                  onChange={handleChange}
                  checked={selectedGroups.includes(key)}
                />
                <label htmlFor={key}>
                  {label}
                </label>
              </li>
            ))}
          </ul>

          <button className="button button--secondary m-t-s" type="submit">
            Confirm
          </button>
        </form>
      )}
      {showTable && <Table {...data} />}
    </div>
  )
})

DataSnapShot.propTypes = {
  country: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired
  })),
}

DataSnapShot.defaultProps = {
  groups: []
}
