import React, { useState } from 'react'
import PropTypes from 'prop-types'

function Filter(props) {
  const { setActiveFilter, filters } = props
  const [activeGroups, setActiveGroups] = useState({})

  const onClickFilterGroup = (group) => {
    const groups = { ...activeGroups }
    if (groups[group]) {
      delete groups[group]
    } else {
      groups[group] = true
    }
    setActiveGroups(groups)
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
                defaultChecked={activeGroups[groupId]}
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
  filters: PropTypes.instanceOf(Object).isRequired,
  setActiveFilter: PropTypes.func.isRequired,
}

export default Filter
