import React from 'react'
import ReactDOM from 'react-dom'
import './TargetAgeGroupInsights.scss'

import Table from './Table'

// mock endpoint until real endpoint created
function mockEndpoint(selectedGroups, cb) {
  function random(min, max) {
    min = Math.ceil(min)
    max = Math.floor(max)
    return Math.floor(Math.random() * (max - min)) + min
  }

  console.log('selectedGroups===', selectedGroups)
  const data = {
    population: random(200, 400),
    cpi: random(100, 300),
    urban: 50,
    rural: 50,
    female: random(30, 80),
    male: random(30, 80),
    internet: random(50, 75),
    targetPopulation: random(200, 300)
  }
  setTimeout(() => {
    cb(data)
  }, 100)
}

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

    // pass selected groups to endpoint
    mockEndpoint(this.state.selectedGroups, (data) => {
      this.setState({
        data
      })
    })
  }

  handleChange = (event) => {
    const { selectedGroups } = this.state
    const value = event.target.value
    const isAlreadySelected = selectedGroups.find((group) => group === value)

    let updatedSelectedGroups = []

    if (isAlreadySelected) {
      updatedSelectedGroups = selectedGroups.filter((group) => group !== value)
    } else {
      updatedSelectedGroups = [...selectedGroups, value]
    }

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
