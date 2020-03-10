import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Sector from './Sector'

const element = document.getElementById('sector-selection')

const uuid = function() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export class SectorChooser extends React.Component {
  constructor(props) {
    super(props);
    this.state = {sectorList: []};
    this.handleClick = this.handleClick.bind(this);
  }

  componentDidMount() {
  }

  componentWillUnmount() {
  }

  handleClick(e) {
    e.preventDefault()
    this.setState({
      sectorList: this.state.sectorList.concat([
        <Sector name='food and drink' key={uuid()}/>
      ])
    })
    console.log(this.state.sectorList);
  }

  render() {
    return (
      <>
        <ul className='sector-list'>
          {this.state.sectorList}
        </ul>
        <button
          type="button"
          className="plus-button"
          onClick={this.handleClick}
          >
          Add a sector
        </button>
      </>
    )
  }
}

SectorChooser.propTypes = {
  name: PropTypes.string
}

export default function createSectorChooser({ element, ...params }) {
  ReactDOM.render(<SectorChooser />, element)
}
