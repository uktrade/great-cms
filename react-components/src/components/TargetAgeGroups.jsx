import React from 'react'
import ReactDOM from 'react-dom'

function renderTable({ population, cpi, urban, rural, female, male, internet, targetPopulation }) {
  return (
    <div className="m-t-m">
      <div className="grid">
        <div className="c-1-4">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Total population</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">{population} million</span>
            </p>
          </figure>
        </div>
        <div className="c-1-4">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Access to internet</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">{internet}% (312.32 million)</span>
            </p>
          </figure>
        </div>
        <div className="c-1-4">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Consumer Price Index</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">{cpi}</span>
            </p>
          </figure>
        </div>
        <div className="c-1-4">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Target age population</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">{targetPopulation} million (100%)</span>
            </p>
          </figure>
        </div>
      </div>

      <div className="grid">
        <div className="c-1-2">
          <div className="statistic__percentage m-b-xs">
            <span style={{ width: `${urban}%` }}></span>
          </div>
          <div className="statistic__group">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Living in urban areas</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{urban}%</span>
              </p>
            </figure>
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Living in rural areas</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{rural}%</span>
              </p>
            </figure>
          </div>
        </div>
        <div className="c-1-2">
          <div className="statistic__percentage m-b-xs">
            <span style={{ width: '51%' }}></span>
          </div>
          <div className="statistic__group">
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Female in target group</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{female} m</span>
              </p>
            </figure>
            <figure className="statistic">
              <figcaption>
                <p className="statistic__caption">Male in target group</p>
              </figcaption>
              <p className="statistic__figure">
                <span className="statistic__details">{male} m</span>
              </p>
            </figure>
          </div>
        </div>
      </div>

      <div className="grid">
        <div className="c-1-2">
          <figure className="statistic">
            <figcaption>
              <p className="statistic__caption">Language</p>
            </figcaption>
            <p className="statistic__figure">
              <span className="statistic__details">Dutch (official); Frisian, Low Saxon,</span>
            </p>
          </figure>
        </div>
      </div>
    </div>
  )
}

function random(min, max) {
  min = Math.ceil(min)
  max = Math.floor(max)
  return Math.floor(Math.random() * (max - min)) + min
}

class TargetAgeGroups extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      isOpen: false,
      selectedGroups: []
    }
  }

  toggleSelector = () => {
    this.setState({ isOpen: !this.state.isOpen })
  }

  submitForm = (event) => {
    event.preventDefault()

    this.toggleSelector()
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
      state: { isOpen, selectedGroups },
      toggleSelector,
      submitForm,
      handleChange
    } = this

    const targetGroupLabels = groups
      .filter((group) => selectedGroups.includes(group['key']))
      .map((group) => group.label)

    const showTable = selectedGroups.length >= 1 && !isOpen

    const buttonText = showTable ? targetGroupLabels.join(', ') : 'Select'

    const urban = random(25, 75)
    const rural = 100 - urban

    return groups ? (
      <>
        <h3>Select target age groups</h3>
        <button className="statistic__details" onClick={toggleSelector}>
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

            <button className="g-button" type="submit">
              Confirm
            </button>
          </form>
        )}
        {showTable &&
          renderTable({
            population: random(200, 400),
            cpi: random(100, 300),
            urban,
            rural,
            female: random(30, 80),
            male: random(30, 80),
            internet: random(50, 75),
            targetPopulation: random(200, 300)
          })}
      </>
    ) : null
  }
}

function createTargetAgeGroups({ element, ...params }) {
  ReactDOM.render(<TargetAgeGroups {...params} />, element)
}

export { TargetAgeGroups, createTargetAgeGroups }
