import React from 'react'
import PropTypes from 'prop-types'


export default class Sector extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      selected: false
    }
    this.handleClick = this.handleClick.bind(this)
  }

  componentDidMount() {
  }

  componentWillUnmount() {
  }

  handleClick(e) {
    e.preventDefault()
    this.setState({selected: this.props.addRemoveSector(e.target.id)})
  }

  render() {
    return (
      <li>
        <button
          className={
            `border-thin border-mid-grey text-mid-grey text-hover-grey bg-hover-stone border-hover-stone pill ${this.state.selected ? 'selected' : ''}`}
          id={this.props.id}
          onClick={this.handleClick}
        >
          {this.props.name}
        </button>
      </li>
    )
  }

}

Sector.propTypes = {
  name: PropTypes.string.isRequired
}
