import React, { useState } from 'react'
import PropTypes from 'prop-types'

const localState = {}

function Filter(props) {
  const { filterId, setActiveFilter, filters } = props

  const onClickFilterGroup = (group) => {
    const groups = { ...(localState[filterId] || {}) }
    if (groups[group]) {
      delete groups[group]
    } else {
      groups[group] = true
    }
    localState[filterId] = groups
    setActiveFilter(groups)
  }

  return (
    <div className="filter">
      <ol className="filter-list body-m m-v-xxs">
        {Object.keys(filters).map((groupId) => {
          return (
            <li key={groupId} className="multiple-choice">
              <input
                onClick={(e) => onClickFilterGroup(groupId, e)}
                type="checkbox"
                className="form-control"
                id={`cb-${groupId}`}
                defaultChecked={(localState[filterId] || {})[groupId]}
              />
              <label htmlFor={`cb-${groupId}`}>
                <span className="form-label">{filters[groupId].label}</span>
              </label>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

Filter.propTypes = {
  filterId: PropTypes.string.isRequired,
  filters: PropTypes.instanceOf(Object).isRequired,
  setActiveFilter: PropTypes.func.isRequired,
}

export default Filter
