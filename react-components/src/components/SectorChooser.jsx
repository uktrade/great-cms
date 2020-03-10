import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Sector from './Sector'

const element = document.getElementById('sector-selection')

export class SectorChooser extends React.Component {
  constructor(props) {

    super(props)

    this.state = {
      sectorList: props.sectorList.map((sector) =>
        <Sector name={sector.name} key={sector.id} id={sector.id} addRemoveSector={this.addRemoveSector} />
      ),
      selectedSectors: [],
      sectorListIsVisible: false,
      tooltipIsVisible: false,
    }

    this.handleClick = this.handleClick.bind(this)
    this.handleMouseOver = this.handleMouseOver.bind(this)
    this.handleMouseOut = this.handleMouseOut.bind(this)
  }

  addRemoveSector = (sector) => {
    if (this.state.selectedSectors.indexOf(sector) == -1) {
      this.setState({selectedSectors: this.state.selectedSectors.concat([sector])})
      return true

    } else {
      const updatedSelectedSectors = this.state.selectedSectors.filter(
        function(item) {
          return item != sector
        }
      )
      this.setState({selectedSectors: updatedSelectedSectors})
      return false
    }
  }

  componentDidMount() {
  }

  componentWillUnmount() {
  }

  showSectorList() {
    this.setState({sectorListIsVisible: true})
  }

  handleClick(e) {
    e.preventDefault()
    this.showSectorList()
  }

  handleMouseOver(e) {
    this.setState({tooltipIsVisible: true})
  }

  handleMouseOut(e) {
    this.setState({tooltipIsVisible: false})
  }

  render() {
    let sectorList;
    if (this.state.sectorListIsVisible) {
      sectorList = (
        <ul className='sector-list'>
          {this.state.sectorList}
        </ul>
      )
    }

    let sectorChooserButton;
    if (!this.state.sectorListIsVisible) {
      sectorChooserButton = (
        <div
          id="sector-chooser"
          className="sector-chooser">
          <div
            aria-hidden={!this.state.tooltipIsVisible}
            id="sector-list-tooltip"
            className={`sector-list-tooltip ${this.state.tooltipIsVisible ? '' : 'visually-hidden'}`}
            role="tooltip">Add sectors</div>
          <button
            type="button"
            className="plus-button"
            onClick={this.handleClick}
            onMouseOver={this.handleMouseOver}
            onMouseOut={this.handleMouseOut}
            aria-describedby="sector-list-tooltip"
            >
            Add a sector
          </button>
        </div>
      )
    }

    return (
      <>
        {sectorList}
        {sectorChooserButton}
      </>
    )
  }
}

SectorChooser.propTypes = {
  sectorList: PropTypes.array.isRequired
}

export default function createSectorChooser({ element, ...params }) {
  ReactDOM.render(<SectorChooser {...params} />, element)
}
