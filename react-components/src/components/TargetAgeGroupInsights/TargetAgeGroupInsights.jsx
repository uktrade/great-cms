import React from 'react'
import ReactDOM from 'react-dom'

import Table from './Table'
import Services from '@src/Services'
import { mapData } from './utils'

class TargetAgeGroupInsights extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      isOpen: false,
      selectedGroups: [],
      data: null
    }
  }

  toggleSelector = () => {
    this.setState({ isOpen: !this.state.isOpen })
  }

  submitForm = (event) => {
    event.preventDefault()
    this.toggleSelector()

    Services.getMarketingCountryData({ country: this.props.country, target_age_groups: this.state.selectedGroups })
      .then((data) =>
        this.setState({
          data: mapData(data)
        })
      )
      .catch((error) => console.log(error))
  }

  handleChange = (event) => {
    const { selectedGroups } = this.state
    const value = event.target.value
    const isAlreadySelected = selectedGroups.find((group) => group === value)
    const updatedSelectedGroups = isAlreadySelected
      ? selectedGroups.filter((group) => group !== value)
      : [...selectedGroups, value]

    this.setState({
      selectedGroups: updatedSelectedGroups
    })
  }

  render() {
    const {
      props: { groups },
      state: { data, isOpen, selectedGroups },
      toggleSelector,
      submitForm,
      handleChange
    } = this

    const targetGroupLabels = groups
      .filter((group) => selectedGroups.includes(group['key']))
      .map((group) => group.label)

    const showTable = selectedGroups.length >= 1 && !isOpen

    return groups ? (
      <div className="target-age-group-insights">
        <h3 className="body-l-b">Select target age groups</h3>
        <button className="button button--secondary button--icon m-t-xs m-r-xs" onClick={toggleSelector}>
          <i className="fa fa-chevron-circle-down" />
          <span>Search</span>
        </button>
        {targetGroupLabels.map(i => <span className='target-age-group-tag body-m-b bg-blue-deep-20'>{i}</span>)}

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
    ) : null
  }
}

function createTargetAgeGroupInsights({ element, ...params }) {
  ReactDOM.render(<TargetAgeGroupInsights {...params} />, element)
}

export { TargetAgeGroupInsights, createTargetAgeGroupInsights }
