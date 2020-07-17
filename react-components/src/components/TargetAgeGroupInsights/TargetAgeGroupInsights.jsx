import React from 'react'
import ReactDOM from 'react-dom'
import './TargetAgeGroupInsights.scss'

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

    Services.getMarketingCountryData({ country: this.props.country, age_group_start: this.state.selectedGroups })
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

    const buttonText = showTable ? targetGroupLabels.join(', ') : 'Select'

    return groups ? (
      <>
        <h3 className="target-age-group-insights__heading">Select target age groups</h3>
        <button className="target-age-group-insights__select-button" onClick={toggleSelector}>
          {buttonText}
        </button>
        {isOpen && (
          <form onSubmit={submitForm}>
            <ul className="form-group select-multiple">
              {groups.map(({ key, label }) => (
                <li className="multiple-choice" key={key}>
                  <input
                    id={key}
                    className="select-multiple"
                    value={key}
                    type="checkbox"
                    onChange={handleChange}
                    checked={selectedGroups.includes(key)}
                  />
                  <label className="form-label" htmlFor={key}>
                    {label}
                  </label>
                </li>
              ))}
            </ul>

            <button className="g-button m-t-s" type="submit">
              Confirm
            </button>
          </form>
        )}
        {showTable && <Table {...data} />}
      </>
    ) : null
  }
}

function createTargetAgeGroupInsights({ element, ...params }) {
  ReactDOM.render(<TargetAgeGroupInsights {...params} />, element)
}

export { TargetAgeGroupInsights, createTargetAgeGroupInsights }
