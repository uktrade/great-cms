import React from 'react'
import PropTypes from 'prop-types'

export default class Sector extends React.Component {
  constructor(props) {
    super(props)

    const { selected } = props

    this.state = {
      selected,
    }
    this.handleClick = this.handleClick.bind(this)
  }

  handleClick() {
    const { selected } = this.state
    const { id, handleSectorButtonClick } = this.props
    this.setState({ selected: !selected })

    handleSectorButtonClick(id)
  }

  render() {
    const { selected } = this.state
    const { id, name } = this.props
    return (
      <li>
        <button
          type="button"
          className={`border-thin border-mid-grey text-mid-grey text-hover-grey bg-hover-stone border-hover-stone pill ${
            selected ? 'selected' : ''
          }`}
          id={id}
          onClick={this.handleClick}
        >
          {name}
        </button>
      </li>
    )
  }
}

Sector.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  selected: PropTypes.bool.isRequired,
  handleSectorButtonClick: PropTypes.func.isRequired,
}
